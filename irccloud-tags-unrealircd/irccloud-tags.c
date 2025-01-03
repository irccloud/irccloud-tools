/*
  Licence: GPLv3 or later
  Based on https://github.com/ValwareIRC/valware-unrealircd-mods/blob/main/kiwiirc-tags/kiwiirc-tags.c
  Copyright © 2022 Valerie Pond
  
  Provides support for IRCCloud-related tags
  Copyright © 2025 IRCCloud
*/
/*** <<<MODULE MANAGER START>>>
module
{
        documentation "https://github.com/irccloud/irccloud-tools/tree/master/irccloud-tags-unrealircd";
        troubleshooting "In case of problems, documentation or e-mail us at team@irccloud.com";
        min-unrealircd-version "6.*";
        max-unrealircd-version "6.*";
        post-install-text {
                "The module is installed. Now all you need to do is add a loadmodule line:";
                "loadmodule \"third/irccloud-tags\";";
                "And /REHASH the IRCd.";
                "The module does not need any other configuration.";
        }
}
*** <<<MODULE MANAGER END>>>
*/

#define MTAG_UNREACT "+draft/unreact"
#define MTAG_EDIT "+draft/edit"
#define MTAG_EDIT_TEXT "+draft/edit-text"
#define MTAG_ATTACHMENTS "+draft/attachments"
#define MTAG_ATTACHMENT_FALLBACK "+draft/attachment-fallback"
#include "unrealircd.h"

ModuleHeader MOD_HEADER =
{
    "third/irccloud-tags",
    "1.0",
    "Provides support for IRCCloud's MessageTags",
    "IRCCloud",
    "unrealircd-6",
};
int irccloud_tag(Client *client, const char *name, const char *value);
void mtag_add_irccloud_tag(Client *client, MessageTag *recv_mtags, MessageTag **mtag_list, const char *signature);

MOD_INIT()
{
    MessageTagHandlerInfo mtag;

    MARK_AS_GLOBAL_MODULE(modinfo);

    memset(&mtag, 0, sizeof(mtag));
    mtag.is_ok = irccloud_tag;
    mtag.flags = MTAG_HANDLER_FLAGS_NO_CAP_NEEDED;
    mtag.name = MTAG_UNREACT;
    MessageTagHandlerAdd(modinfo->handle, &mtag);

    memset(&mtag, 0, sizeof(mtag));
    mtag.is_ok = irccloud_tag;
    mtag.flags = MTAG_HANDLER_FLAGS_NO_CAP_NEEDED;
    mtag.name = MTAG_EDIT;
    MessageTagHandlerAdd(modinfo->handle, &mtag);

    memset(&mtag, 0, sizeof(mtag));
    mtag.is_ok = irccloud_tag;
    mtag.flags = MTAG_HANDLER_FLAGS_NO_CAP_NEEDED;
    mtag.name = MTAG_EDIT_TEXT;
    MessageTagHandlerAdd(modinfo->handle, &mtag);

    memset(&mtag, 0, sizeof(mtag));
    mtag.is_ok = irccloud_tag;
    mtag.flags = MTAG_HANDLER_FLAGS_NO_CAP_NEEDED;
    mtag.name = MTAG_ATTACHMENTS;
    MessageTagHandlerAdd(modinfo->handle, &mtag);

    memset(&mtag, 0, sizeof(mtag));
    mtag.is_ok = irccloud_tag;
    mtag.flags = MTAG_HANDLER_FLAGS_NO_CAP_NEEDED;
    mtag.name = MTAG_ATTACHMENT_FALLBACK;
    MessageTagHandlerAdd(modinfo->handle, &mtag);

    HookAddVoid(modinfo->handle, HOOKTYPE_NEW_MESSAGE, 0, mtag_add_irccloud_tag);
    

    return MOD_SUCCESS;
}

MOD_LOAD()
{
    return MOD_SUCCESS;
}

MOD_UNLOAD()
{
    return MOD_SUCCESS;
}

int irccloud_tag(Client *client, const char *name, const char *value)
{
    if (!strlen(value))
    {
        sendto_one(client, NULL, "FAIL * MESSAGE_TAG_TOO_SHORT %s :That message tag must contain a value.", name);
        return 0;
    }
    return 1;
}

void mtag_add_irccloud_tag(Client *client, MessageTag *recv_mtags, MessageTag **mtag_list, const char *signature)
{
    MessageTag *m;

    if (IsUser(client))
    {
        m = find_mtag(recv_mtags, MTAG_UNREACT);
        if (m)
        {
            m = duplicate_mtag(m);
            AddListItem(m, *mtag_list);
        }
        m = find_mtag(recv_mtags, MTAG_EDIT);
        if (m)
        {
            m = duplicate_mtag(m);
            AddListItem(m, *mtag_list);
        }
        m = find_mtag(recv_mtags, MTAG_EDIT_TEXT);
        if (m)
        {
            m = duplicate_mtag(m);
            AddListItem(m, *mtag_list);
        }
        m = find_mtag(recv_mtags, MTAG_ATTACHMENTS);
        if (m)
        {
            m = duplicate_mtag(m);
            AddListItem(m, *mtag_list);
        }
        m = find_mtag(recv_mtags, MTAG_ATTACHMENT_FALLBACK);
        if (m)
        {
            m = duplicate_mtag(m);
            AddListItem(m, *mtag_list);
        }
    }
}
