import logging
import os.path
from pathlib import Path
import jinja2
from pollin.System.common.DigitalObjectViewModel import DigitalObjectViewModel
from pollin.System.init.ApplicationContext import ApplicationContext

class ApplicationViewTemplateRenderer:
    """
    Handles the rendering of views for the application, like about.html or contact.html
    based on template files in the view templates pages directory.
    """

    app_context: ApplicationContext
    """
    The application context
    """


    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context



    def render(self):
        """
        Renders the views for application based data
        :param project_data: metadata of the GAMS project
        """
        # accessing information from the application context
        output_dir = self.app_context.get_config().project_public_dir
        template_pages_dir = self.app_context.get_config().project_src_view_template_pages_dir
        view_template_dir = self.app_context.get_config().project_src_view_template_dir
        project_data = self.app_context.get_app_data_store().get_project_data()


        # template names = relative path to the view template directory
        environment = jinja2.Environment(loader=jinja2.FileSystemLoader(view_template_dir))

        # the material digital object is automatically bound to the /pages/ views.
        # TODO find first object that contains in id 'memo.material'
        objects = self.app_context.get_app_data_store().get_objects()
        # TODO refactor this assignment
        material_object = DigitalObjectViewModel({}, {}, {}, {})
        for object in objects:
            project_abbr = self.app_context.get_config().project
            if object.db["id"] == f'{project_abbr}.material':
                material_object = object
                break


        pages = Path(template_pages_dir).glob('*.j2')
        for page in pages:
            # get the relative path to the view template directory
            template_path = Path(page).relative_to(view_template_dir)
            # thymeleaf expects forward slashes
            template_path = str(template_path).replace(os.sep, '/')

            template = environment.get_template( template_path )

            content = template.render(project=project_data, object=material_object)
            output_path = Path(output_dir).joinpath(page.stem + '.html')
            logging.info(f"Rendering {page.name} to {output_path}")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
