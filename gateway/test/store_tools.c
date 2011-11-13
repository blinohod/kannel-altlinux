/* ====================================================================
 * The Kannel Software License, Version 1.0
 *
 * Copyright (c) 2001-2008 Kannel Group
 * Copyright (c) 1998-2001 WapIT Ltd.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * 3. The end-user documentation included with the redistribution,
 *    if any, must include the following acknowledgment:
 *       "This product includes software developed by the
 *        Kannel Group (http://www.kannel.org/)."
 *    Alternately, this acknowledgment may appear in the software itself,
 *    if and wherever such third-party acknowledgments normally appear.
 *
 * 4. The names "Kannel" and "Kannel Group" must not be used to
 *    endorse or promote products derived from this software without
 *    prior written permission. For written permission, please
 *    contact org@kannel.org.
 *
 * 5. Products derived from this software may not be called "Kannel",
 *    nor may "Kannel" appear in their name, without prior written
 *    permission of the Kannel Group.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESSED OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED.  IN NO EVENT SHALL THE KANNEL GROUP OR ITS CONTRIBUTORS
 * BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
 * OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
 * OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 * BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
 * OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * ====================================================================
 *
 * This software consists of voluntary contributions made by many
 * individuals on behalf of the Kannel Group.  For more information on
 * the Kannel Group, please see <http://www.kannel.org/>.
 *
 * Portions of this software are based upon software originally written at
 * WapIT Ltd., Helsinki, Finland for the Kannel project.
 */

/*
 * Simple tool that allows listing and basic manipulation of a kannel storefile.
 *
 * Alejandro Guerrieri <aguerrieri at kannel dot org>
 *
 */

#include <errno.h>
#include "gwlib/gwlib.h"
#include "shared.h"
#include "bearerbox.h"

#define DEFAULT_LOG_LEVEL 2
#define DEFAULT_LIST_LIMIT 100

#define COMMAND_LIST 1
#define COMMAND_DELETE 2
#define COMMAND_EXPORT 3

static long counter = 0;
static long list_from;
static long list_limit;
static int command;
static Octstr *param_1;
static Octstr *param_2;
static Octstr *conf_file;
static Cfg *cfg;
static List *list;
static FILE *file = NULL;

#define PRINT_COLUMNS(sep, trim, col1, col2, col3, col4, col5) \
	char *head, *mid, *foot; \
	asprintf(&head, "%s%s", sep, trim); \
	asprintf(&mid, "%s%s%s", trim, sep, trim); \
	asprintf(&foot, "%s%s", trim, sep); \
	printf("%s%-36s%s%-10s%s%-10s%s%-14s%s%-50s%s\n", head, col1, mid, col2, mid, col3, mid, col4, mid, col5, foot);

/*
 * Returns chr repeated num times
 */
char *repeat_char(char *chr, int num) {
	int i;
	char *ret = (char*)gw_malloc(num + 1);
	for(i=0;i<num;i++) {
		strncat(ret, chr, 1);
	}
	return ret;
}

/*
 * Prints a separation line
 */
void print_sep() {
	PRINT_COLUMNS("+", "-", repeat_char("-", 36), \
		repeat_char("-", 10), repeat_char("-", 10),repeat_char("-", 14), \
		repeat_char("-", 50));
}

/*
 * Prints a nicely formatted header
 */
void print_header() {
	print_sep();
	PRINT_COLUMNS("|", " ", "message id", "from", "to", "smsc", "text");
	print_sep();
}

/*
 * Callback function that prints a message from the store
 */
static void print_msg(Msg *msg)
{
	char buf[UUID_STR_LEN + 1];
	counter++;
	if (counter > list_from && counter <= list_limit) {
		uuid_unparse(msg->sms.id, buf); \
		printf("| %-36s | %-10s | %-10s | %-14s | %-50s |\n",
			buf,
			octstr_get_cstr(msg->sms.sender),
			octstr_get_cstr(msg->sms.receiver),
			octstr_get_cstr(msg->sms.smsc_id),
			octstr_get_cstr(msg->sms.msgdata)
		);
	}
}

static void msg_count(Msg *msg) {
	counter++;
}

static void msg_push(Msg *msg) {
	Octstr *os;
	os = msg_pack(msg);
	gwlist_append(list, os);
	//octstr_destroy(os);
}

/* void function to make gwlib happy */
static int check_args(int j, int argc, char **argv) {
	int i;
	command = 0;
	for (i=j; i < argc; i++) {
		if (strcmp(argv[i],"-c")==0 || strcmp(argv[i],"--conf")==0) {
			if (i+1 < argc) {
				conf_file = octstr_create(argv[i+1]);
				i++;
			} else {
				panic(0, "Missing argument for option %s\n", argv[i]);
			}
		} else if (strcmp(argv[i],"list")==0) {
			command = COMMAND_LIST;
			i++;
			if (i < argc) {
				list_limit = atol(argv[i]);
				i++;
				if (i < argc) {
					list_from = list_limit-1;
					list_limit = atol(argv[i]);
				} else {
					list_from = 0;
				}
			} else {
				list_from = 0;
				list_limit = DEFAULT_LIST_LIMIT;
			}
			if (list_limit < 0 || list_from < 0)
				return -1;
			list_limit += list_from;
			return 0;
		} else if (strcmp(argv[i],"delete")==0) {
			command = COMMAND_DELETE;
			i++;
			if (i < argc) {
				param_1 = octstr_create(argv[i]);
			} else {
				panic(0, "Missing argument for option %s\n", argv[i-1]);
			}
			return 0;
		} else if (strcmp(argv[i],"export")==0) {
			command = COMMAND_EXPORT;
			i++;
			if (i < argc) {
				param_1 = octstr_create(argv[i]);
				i++;
				if (i < argc) {
					param_2 = octstr_create(argv[i]);
				} else {
					panic(0, "Missing second argument for option %s\n", argv[i-2]);
				}
			} else {
				panic(0, "Missing both arguments for option %s\n", argv[i-1]);
			}
			return 0;
		} else {
			return -1;
		}
	}
    return 0;
}

void print_usage(char *arg) {
	printf("Usage: %s [-c conf-file] <command> [options]\n\n"
			"Examples:\n"
			"%s list [from] [to]\n"
			"%s export <text/html/xml/spool/file> <location>\n"
			"%s delete <uid>\n", arg, arg, arg, arg);
}

int main(int argc, char **argv)
{
	char id[UUID_STR_LEN + 1];
    int cf_index, ret, type;
    Octstr *os, *store_type, *store_location, *status;
	Msg *msg;
	CfgGroup *grp;

	conf_file = NULL;

    gwlib_init();

    //This can be overwritten with the -v flag at runtime
    log_set_output_level(DEFAULT_LOG_LEVEL);

    cf_index = get_and_set_debugs(argc, argv, check_args);

    if (argv[cf_index] == NULL) {
        print_usage(argv[0]);
        goto error;
    }

    if (conf_file == NULL)
    	conf_file = octstr_create("kannel.conf");

    cfg = cfg_create(conf_file);

    if (cfg_read(cfg) == -1)
    	panic(0, "Couldn't read configuration from `%s'.", octstr_get_cstr(conf_file));
	info(0, "1");
    grp = cfg_get_single_group(cfg, octstr_imm("core"));
    if (grp == NULL) {
    	printf("FATAL: Could not load Kannel's core group. Exiting.\n");
    	return 2;
    }

    store_location = cfg_get(grp, octstr_imm("store-location"));
    store_type = cfg_get(grp, octstr_imm("store-type"));

    store_init(store_type, store_location, -1, msg_pack, msg_unpack_wrapper);

    switch (command) {
    case COMMAND_LIST:
    	printf("Listing records %d -> %d\n", list_from+1, list_limit);
    	print_header();
		store_load(print_msg);
		if (counter == 0) {
			printf("|%60s%14s%60s|\n", "", "Store is Empty", "");
		}
		print_sep();
		break;
    case COMMAND_DELETE:
    	store_load(msg_count);
    	msg = msg_create(ack);
    	msg->ack.nack = ack_failed;
    	msg->ack.time = time(NULL);
    	uuid_parse(octstr_get_cstr(param_1), msg->ack.id);
    	ret = store_save(msg);
        if (ret == 0) {
        	printf("Deleted message %s\n", octstr_get_cstr(param_1));
        	counter--;
        } else {
        	printf("Could not delete message %s\n", octstr_get_cstr(param_1));
        }
        msg_destroy(msg);
		break;
    case COMMAND_EXPORT:
    	counter = 0;
    	type = 0;
    	list = gwlist_create();
    	store_load(msg_push);
    	printf("Exporting %ld messages...\n", gwlist_len(list));
    	if ((octstr_compare(param_1, octstr_imm("file")) == 0) ||
    		(octstr_compare(param_1, octstr_imm("spool")) == 0)) {
        	store_shutdown();
        	store_init(param_1, param_2, -1, msg_pack, msg_unpack_wrapper);
        	store_load(msg_count);
        	while ((os = gwlist_extract_first(list)) != NULL) {
        		msg = msg_unpack_wrapper(os);
        		if (msg != NULL) {
    				ret = store_save(msg);
    				if (ret == 0) {
    					counter++;
    				} else {
    					printf("Error saving message\n");
    				}
        		} else {
        			printf("Error extracting message\n");
        		}
        		msg_destroy(msg);
        	}
        	status = NULL;
    	} else if (octstr_compare(param_1, octstr_imm("text")) == 0) {
    		status = store_status(BBSTATUS_TEXT);
    	} else if (octstr_compare(param_1, octstr_imm("html")) == 0) {
    		status = store_status(BBSTATUS_HTML);
    	} else if (octstr_compare(param_1, octstr_imm("xml")) == 0) {
    		status = store_status(BBSTATUS_XML);
		} else {
			status = NULL;
		}
    	if (status != NULL) {
    	    file = fopen(octstr_get_cstr(param_2), "w");
    	    if (file == NULL) {
    	        error(errno, "Failed to open '%s' for writing, cannot create output file",
    		      octstr_get_cstr(param_2));
    	        return -1;
    	    }
    	    octstr_print(file, status);
    	    fflush(file);
    	    if (file != NULL)
    	    	fclose(file);
    		//printf("%s", octstr_get_cstr(status));
    	}
    	gwlist_destroy(list, octstr_destroy_item);

		break;
    default:
    	break;
    }

    octstr_destroy(store_type);
    octstr_destroy(store_location);
    cfg_destroy(cfg);
    store_shutdown();
error:
    gwlib_shutdown();

    return 1;
}

