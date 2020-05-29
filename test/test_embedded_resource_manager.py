import sys, os
sys.path.append(os.getcwd())
from plugins.embedded_resource_manager import EmbeddedResourceManager
import unittest

class client:
    def request(self):
        pass

class TestERM(unittest.TestCase):
    def setUp(self):
        self.host = "http://localhost"
        self.client = client()
        self.erm = EmbeddedResourceManager(self)

    def test_base(self):
        content = """
        <html>
            <head>
                <base href="http://basehost">
                <link rel="stylesheet" href="style.css">
            </head>
            <body>
            </body>
        </html>
        """
        resources = self.erm.get_embedded_resources(content)
        self.assertRegex(resources[0],"http:\/\/basehost\/style.css")

    def test_resource_count(self):
        content = """
        <html>
            <head>
                <link rel="stylesheet" href="style.css">
            </head>
            <body>
                <script src="myscript.js"></script>
                <img src="myimage.png">
            </body>
        </html>
        """
        resources = self.erm.get_embedded_resources(content)
        self.assertEqual(len(resources), 3)

    def test_style(self):
        content = """
        <html>
            <head>
                <style>
                    .cheesy {background-image: URL("cheese.gif");;}
                </style>
            </head>
            <body>
            </body>
        </html>
        """
        resources = self.erm.get_embedded_resources(content)
        self.assertRegex(resources[0],"http:\/\/localhost\/cheese.gif")

    def test_all_types(self):
        content = """
        <html>
            <head>
                <link rel="stylesheet" href="style.css">
                <link rel="STYLESHEET" href="ucase_style.css">
                <link rel="Stylesheet" href="cap_style.css">
            </head>
            <body background="background.png">
                <script src="myscript.js"></script>
                <img src="myimage.png">
                <video width="100" height="100" controls>
                    <source src="embedded_video.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                <embed type="image/jpg" src="embedded_image.jpg" width="100" height="100">
                <form>
                    <input type="image" src="form_image.png">
                    <input type="IMAGE" src="form_ucase_image.png">
                    <input type="Image" src="form_cap_image.png">
                </form>
                <object data="object_image.jpg" width="100" height="100"></object>
                <iframe src="https://framed_page/index.html"></iframe>
            </body>
        </html>
        """
        resources = self.erm.get_embedded_resources(content)
        self.assertIn("http://localhost/style.css",resources)
        self.assertIn("http://localhost/ucase_style.css",resources)
        self.assertIn("http://localhost/cap_style.css",resources)
        self.assertIn("http://localhost/background.png",resources)
        self.assertIn("http://localhost/myscript.js",resources)
        self.assertIn("http://localhost/myimage.png",resources)
        self.assertIn("http://localhost/embedded_video.mp4",resources)
        self.assertIn("http://localhost/embedded_image.jpg",resources)
        self.assertIn("http://localhost/form_image.png",resources)
        self.assertIn("http://localhost/form_ucase_image.png",resources)
        self.assertIn("http://localhost/form_cap_image.png",resources)
        self.assertIn("http://localhost/object_image.jpg",resources)
        self.assertIn("https://framed_page/index.html",resources)


if __name__ == '__main__':
    unittest.main()