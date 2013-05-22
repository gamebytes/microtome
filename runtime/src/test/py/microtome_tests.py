#
# microtome

import logging
import os.path

import microtome.xml_support
import microtome.ctx
from microtome.library import Library
from primitive_page import PrimitivePage
from list_page import ListPage
from annotation_page import AnnotationPage
from ref_page import RefPage

from microtome.error import MicrotomeError

LOG = logging.getLogger("tests")

def resource(name):
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", name)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        lib = Library()
        ctx = microtome.ctx.create_ctx()
        ctx.register_page_classes([PrimitivePage, ListPage, AnnotationPage, RefPage])
        readers = microtome.xml_support.readers_from_files(
            resource("AnnotationTest.xml"),
            resource("ListTest.xml"),
            # resource("NestedTest.xml"),
            # resource("ObjectTest.xml"),
            resource("PrimitiveTest.xml"),
            resource("RefTest.xml"),
            resource("TemplateTest.xml"),
            resource("TomeTest.xml"))
        ctx.load(lib, readers)
        LOG.info(lib.get("primitiveTest").foo)
        LOG.info(len(lib.get("listTest").kids))
        LOG.info(lib.get("listTest").kids[1].bar)
        LOG.info(lib.get("annotationTest").primitives)
        LOG.info(lib.get("annotationTest").bar)
        LOG.info(lib.get("refTest").nested.baz)
        LOG.info(lib.get("templateTest2").bar)
        LOG.info(lib.get("templateTest2").baz)
    except MicrotomeError as e:
        print e.stacktrace
