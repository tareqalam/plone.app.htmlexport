# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
import os
import shutil
from BeautifulSoup import BeautifulSoup
try:
    from plone.app.htmlexport import config
except:
    raise ImportError('config.py must be created inside plone.app.htmlexport, see example in config.py.example')


class HTMLExport(BrowserView):
    root_dir = '/tmp/'

    def parse(self, obj):
        html = obj.view()
        soup = BeautifulSoup(html)
        # import pdb;pdb.set_trace()
        head = soup.find('head')
        head.append('<meta name="URL" content="%s" />' % obj.absolute_url())

        return soup.prettify()

    def parse_image(self, obj):
        return obj.download()

    def parse_video(self, obj):
        filename = obj.video_file.filename
        data = obj.video_file.data.data
        return filename, data

    def parse_file(self, obj):
        # import pdb;pdb.set_trace()
        filename = obj.getFile().filename
        data = obj.getFile().data.data
        return filename, data

    def go_deep_and_parse(self, base_dir, parent):
        objects = parent.objectValues()
        for obj in objects:
            portal_type = obj.portal_type

            if portal_type in config.folderish_types:
                base_dir = self.root_dir + '/'.join(obj.getPhysicalPath())
                os.makedirs(base_dir)
                self.go_deep_and_parse(base_dir, obj)
            elif portal_type in config.entry_types:
                html = self.parse(obj)
                base_dir = self.root_dir + '/'.join(obj.getPhysicalPath())
                fp = open(base_dir + '.html', 'w')
                fp.write(html)
                fp.close()
            elif portal_type in config.image_types:
                img = self.parse_image(obj)
                fp = open(base_dir + '/' + obj.getId(), 'w')
                fp.write(img)
                fp.close()
            elif portal_type in config.video_types:
                videofilename, videofiledata = self.parse_video(obj)
                fp = open(base_dir + '/' + videofilename, 'w')
                fp.write(videofiledata)
                fp.close()
            elif portal_type in config.file_types:
                filename, filedata = self.parse_file(obj)
                base_dir = self.root_dir + '/'.join(obj.getPhysicalPath()[:-1])
                fp = open(base_dir + '/' + filename, 'w')
                fp.write(filedata)
                fp.close()
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
        self.context.MailHost.send('done export to location of server: %s' % base_dir, 'tareq.mist@gmail.com', 'info@localhost', 'htmlexport done')

        return 'done'