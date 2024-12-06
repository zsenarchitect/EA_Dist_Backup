from pyrevit import forms
from EnneadTab import EMAIL


class EmailData(object):
    def __init__(self, receiver_list, subject, body, is_adding_final_folder_link, embeded_images_list = None, additional_attachments_list = None):

        self.receiver_list = receiver_list
        self.subject = subject
        self.body = body
        self.is_adding_final_folder_link = is_adding_final_folder_link
        self.embeded_images_list = embeded_images_list
        self.additional_attachments_list = additional_attachments_list
        self.log_file_path = None

    def update_info(self, EXPORTER_UI):

        self.receiver_list = EXPORTER_UI.email_receivers.Text
        self.subject = EXPORTER_UI.email_subject_line.Text
        self.body = EXPORTER_UI.email_body.Text
        self.is_adding_final_folder_link = EXPORTER_UI.checkbox_add_folder_link.IsChecked
        self.body_folder_link_list = [EXPORTER_UI.copy_folder_path]
        if hasattr(EXPORTER_UI, "log_file_path"):
            self.log_file_path = EXPORTER_UI.log_file_path

    def update_attachments(self):
        attachments_list = forms.pick_file(file_ext = '*', restore_dir = True, multi_file = True, title = "Pick attachments")
        if not attachments_list:
            return
        self.additional_attachments_list = attachments_list

    def update_embeded_image(self):
        images_list = forms.pick_file(file_ext = '*', restore_dir = True, multi_file = True, title = "Pick images to embed in Email.")
        if not images_list:
            return
        self.embeded_images_list = images_list

    def send(self):
        if self.additional_attachments_list:
            self.additional_attachments_list = filter(lambda item: not(item is None or "autosave log" in item.lower()), self.additional_attachments_list)

            self.additional_attachments_list.append(self.log_file_path)
        else:
            self.additional_attachments_list = [self.log_file_path]


        #print self.additional_attachments_list
        EMAIL.email(receiver_email_list = self.receiver_list,
                    subject = self.subject,
                    body = self.body,
                    body_folder_link_list = self.body_folder_link_list,
                    body_image_link_list = self.embeded_images_list,
                    attachment_list = self.additional_attachments_list)