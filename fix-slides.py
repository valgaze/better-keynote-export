#!/usr/bin/env python
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
import sys
import os
from glob import glob
import appscript
from argparse import ArgumentParser
from contextlib import closing


class SlideFixer(object):
    def __init__(self, keynote, notes, outdir):
        self.keynote = os.path.abspath(keynote)
        print self.keynote
        self.notes = notes
        self.outdir = os.path.abspath(outdir)
    
    def run(self):
        self.make_dirs()
        self.export()
        self.emit_pdf()

    @property
    def slidesdir(self):
        return os.path.join(self.outdir, 'slides')

    @property
    def outfile(self):
        return os.path.join(self.outdir, 'out.pdf')
        
    def make_dirs(self):
        for d in (self.outdir, self.slidesdir,):
            if not os.path.isdir(d):
                os.mkdir(d)
        
    def emit_pdf(self):
        s = ParagraphStyle('note')
        s.textColor = 'black'
        s.alignment = TA_LEFT
        s.fontSize = 24
        s.leading = 24

        notes = open(self.notes, 'r').read().split('\n\n')
        c = canvas.Canvas(self.outfile, pagesize=(1024, 1024))
        c.setFont('Courier', 80)
        c.setStrokeColorRGB(0,0,0)
        sbot = 1024 - 768
        for slide, note in zip(glob('%s/*jpg' % self.slidesdir), notes):
            c.drawImage(slide, 0, sbot)
            c.line(0, sbot, 1024, sbot)
            if note:
                p = Paragraph(note, s)
                p.wrapOn(c, 1000, sbot)
                p.breakLines(1000)
                p.drawOn(c, 10, sbot - 10)
            c.showPage()
        c.save()

    def export(self):            
        keynote = appscript.app('Keynote')
        outpath = appscript.mactypes.File(self.slidesdir)
        k = appscript.k
        keynote_file = appscript.mactypes.File(self.keynote)
        with closing(keynote.open(keynote_file)) as doc:
            doc.export(as_=k.slide_images, to=outpath, with_properties = {
                k.export_style: k.IndividualSlides,
                k.compression_factor: 0.9,
                k.image_format: k.JPEG,
                k.movie_format: k.large,
                k.all_stages: True,
                k.skipped_slides: False
            })
        

def main():
    ap = ArgumentParser()
    ap.add_argument('-k', '--keynote', help="Path to the keynote to convert")
    ap.add_argument('-n', '--notes', help="Path to the notes file.")
    ap.add_argument('-o', '--outdir', help="Where to put the output.")
    args = ap.parse_args()
    SlideFixer(args.keynote, args.notes, args.outdir).run()
    

if __name__ == '__main__':    
    main()
