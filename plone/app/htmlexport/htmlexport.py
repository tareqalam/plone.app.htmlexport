# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
import os
import shutil
from BeautifulSoup import BeautifulSoup
try:
    from plone.app.htmlexport import config
except:
    raise ImportError('config.py must be created inside plone.app.htmlexport, see example in config.py.example')

# http://admin4:*password*@localhost:8088/help/basics/video-resources/insite-training-part-3-resources/downloadfile?filefield=video_file
class DownloadFile(BrowserView):
    def __call__(self):
        # import pdb;pdb.set_trace()
        context = self.context
        filefield = self.context.REQUEST.get('filefield')
        field = context.getField(filefield)
        return field.download(context)


class HTMLExport(BrowserView):
    root_dir = config.root_dir

    def parse(self, obj):
        view_method = obj.defaultView()
        html = getattr(obj, view_method)()
        soup = BeautifulSoup(html)
        # import pdb;pdb.set_trace()
        # head = soup.find('head')
        # head.append('<meta name="URL" content="%s" />' % obj.absolute_url())

        content = soup.find("div", {"class": "documentContent"})
        link_parent = content.find('a', {'class': 'link-parent'})
        if link_parent:
            link_parent.replaceWith('')
        documentActions = content.find('div', {'class': 'documentActions'})
        if documentActions:
            documentActions.replaceWith('')
        portalMessage = content.find('dl', {'id': 'kssPortalMessage'})
        if portalMessage:
            portalMessage.replaceWith('')

        viewlet_above_content = content.find('div', {'id': 'viewlet-above-content'})
        if viewlet_above_content:
            viewlet_above_content.replaceWith('')
        jumpBox = content.find('div', {'class': 'jumpBox'})
        if jumpBox:
            jumpBox.replaceWith('')
        if not content:
            raise

        head_extra = '<meta name="URL" content="%s" />' % obj.absolute_url()
        parsed_html = '<html><head>%s</head><body>' % head_extra
        # import pdb;pdb.set_trace()
        parsed_html += content.prettify()
        parsed_html += '</body></html>'
        return parsed_html

        # return soup.prettify()

    def get_url_with_pass(self, url):
        return url.replace(config.hostname, '%s:%s@%s' % (config.username, config.password, config.hostname))

    def parse_image(self, obj):
        # import pdb;pdb.set_trace()
        filename = obj.getImage().filename
        # data = obj.video_file.data.data
        url = self.get_url_with_pass(obj.absolute_url()) + '/downloadfile?filefield=image'
        print url
        os.system("wget -O '/tmp/%s' --timeout=6000 %s" % (filename, url))

        return filename

    def parse_video(self, obj):
        filename = obj.video_file.filename
        # data = obj.video_file.data.data
        url = self.get_url_with_pass(obj.absolute_url()) + '/downloadfile?filefield=video_file'
        print url
        os.system("wget -O '/tmp/%s' --timeout=6000 %s" % (filename, url))

        return filename

    # def parse_doc_file(self, obj):
    #    # data = obj.getFile().data.data
    #    # url = 'http://admin4:admin4@localhost:8088/help/personnel/help-files/affiliation-of-people/adding-an-affiliated-person/at_download/file'
    #    url = self.get_url_with_pass(obj.absolute_url()) + '/downloadfile?filefield=file'
    #    print url
    #    os.system("wget -O '/tmp/%s' %s" % (obj.getFile().filename, url))
    #    return None

    def parse_file(self, obj):
        # import pdb;pdb.set_trace()
        filename = obj.getFile().filename
        url = self.get_url_with_pass(obj.absolute_url()) + '/downloadfile?filefield=file'
        print url
        os.system("wget -O '/tmp/%s' %s" % (filename, url))
        return filename

    def go_deep_and_parse(self, base_dir, parent):
        objects = parent.objectValues()
        if len(objects) == 0:
            objects = [parent]
        for obj in objects:
            portal_type = obj.portal_type

            if portal_type in config.folderish_types:
                base_dir = self.root_dir + '/'.join(obj.getPhysicalPath())
                try:
                    os.makedirs(base_dir)
                    self.go_deep_and_parse(base_dir, obj)
                except:
                    pass

            elif portal_type in config.entry_types:
                html = self.parse(obj)
                base_dir = self.root_dir + '/'.join(obj.getPhysicalPath())
                fp = open(base_dir + '.html', 'w')
                fp.write(html)
                fp.close()
            elif portal_type in config.image_types:
                # img = self.parse_image(obj)
                # fp = open(base_dir + '/' + obj.getId(), 'w')
                # fp.write(img)
                # fp.close()
                imgfilename = self.parse_image(obj)
                base_dir = self.root_dir + '/'.join(obj.getPhysicalPath()[:-1])
                move_to = base_dir + '/' + imgfilename
                os.system('mv "/tmp/%s" "%s"' % (imgfilename, move_to))
            elif portal_type in config.video_types:
                videofilename = self.parse_video(obj)
                base_dir = self.root_dir + '/'.join(obj.getPhysicalPath()[:-1])
                move_to = base_dir + '/' + videofilename
                os.system('mv "/tmp/%s" "%s"' % (videofilename, move_to))
            elif portal_type in config.file_types:
                filename = self.parse_file(obj)
                base_dir = self.root_dir + '/'.join(obj.getPhysicalPath()[:-1])
                move_to = base_dir + '/' + filename
                os.system('mv "/tmp/%s" "%s"' % (filename, move_to))

            elif portal_type in config.ignore_types:
                self.context.plone_log('id: %s, ignore %s' % (obj.getId(), portal_type))
            else:
                raise RuntimeError(portal_type + ' missing!')

    def __call__(self):

        base_dir = self.root_dir + '/'.join(self.context.getPhysicalPath())

        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)
        os.makedirs(base_dir)
        self.go_deep_and_parse(base_dir, self.context)
        try:
            self.context.MailHost.send('done export to location of server: %s' % base_dir, config.after_done_send_mail_to, config.from_mail, 'htmlexport done')
        except:
            pass

        return 'done'
