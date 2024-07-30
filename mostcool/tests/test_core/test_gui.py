import pytest
from unittest import mock
from tkinter import Tk, Canvas, Button
from mostcool.core.gui import MyApp, ImageViewer  

@pytest.fixture
def app():
    """Fixture to initialize the MyApp instance."""
    app = MyApp()
    yield app
    app.root.destroy()  # Cleanup after test

def test_app_initialization(app):
    """Test if the MyApp instance initializes correctly."""
    assert isinstance(app.root, Tk)
    assert app.main_notebook is not None

def test_image_viewer_initialization():
    """Test if the ImageViewer instance initializes correctly."""
    root = Tk()
    image_folder = "/app/mostcool/assets/images/v1_slide_images"
    with mock.patch('os.listdir', return_value=['Slide01.jpg', 'Slide02.jpg', 'Slide03.jpg']):
        viewer = ImageViewer(root, image_folder)
        assert viewer.main == root
        assert viewer.image_folder == image_folder
    root.destroy()

def test_show_next_image():
    """Test the show_next_image method of ImageViewer."""
    root = Tk()
    image_folder = "/app/mostcool/assets/images/v1_slide_images"
    with mock.patch('os.listdir', return_value=['Slide01.jpg', 'Slide02.jpg', 'Slide03.jpg']):
        viewer = ImageViewer(root, image_folder)
        viewer.image_files = ["image1.jpg", "image2.jpg", "image3.jpg"]
        viewer.current_image = 0

        with mock.patch.object(viewer, 'load_image', return_value=None) as mock_load_image:
            viewer.show_next_image()
            assert viewer.current_image == 1
            viewer.show_next_image()
            assert viewer.current_image == 2
            viewer.show_next_image()
            assert viewer.current_image == 2  # Should remain the same
    root.destroy()

def test_show_prev_image():
    """Test the show_prev_image method of ImageViewer."""
    root = Tk()
    image_folder = "/app/mostcool/assets/images/v1_slide_images"
    with mock.patch('os.listdir', return_value=['Slide01.jpg', 'Slide02.jpg', 'Slide03.jpg']):
        viewer = ImageViewer(root, image_folder)
        viewer.image_files = ["image1.jpg", "image2.jpg", "image3.jpg"]
        viewer.current_image = 2

        with mock.patch.object(viewer, 'load_image', return_value=None) as mock_load_image:
            viewer.show_prev_image()
            assert viewer.current_image == 1
            viewer.show_prev_image()
            assert viewer.current_image == 0
            viewer.show_prev_image()
            assert viewer.current_image == 0  # Should remain the same
    root.destroy()

def test_client_run(app):
    """Test the client_run method to ensure the thread starts correctly."""
    with mock.patch('mostcool.core.gui.simulator.Simulator') as mock_simulator:
        mock_instance = mock_simulator.return_value
        mock_instance.run = mock.Mock()
        app.idf_path.set("/path/to/idf")
        app.epw_path.set("/path/to/epw")
        app.control_option.set("Control Option")
        app.datacenter_location.set("Datacenter Location")
        app.client_run()
        mock_instance.run.assert_called_once()
        assert app.long_thread is not None

def test_open_paraview(app):
    """Test the open_paraview method."""
    with mock.patch('mostcool.core.gui.paraview.predict_temperature') as mock_predict:
        app.paraview_velocity.set("5")
        app.paraview_CPU_load_fraction.set("0.8")
        app.paraview_server_temp_in.set("25")
        app.open_paraview()
        mock_predict.assert_called_once_with(velocity=5, CPU_load_fraction=0.8, inlet_server_temperature=25)
