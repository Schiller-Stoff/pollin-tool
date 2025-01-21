import logging
import os.path
from pathlib import Path
import jinja2
from pollin.System.init.ApplicationContext import ApplicationContext
from pollin.System.watch.render.ApplicationErrorHtmlBuilder import ApplicationErrorHtmlBuilder


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

        project_abbr = self.app_context.get_config().project

        pages = Path(template_pages_dir).glob('*.j2')
        for page in pages:
            # get the relative path to the view template directory
            template_path = Path(page).relative_to(view_template_dir)
            # thymeleaf expects forward slashes
            template_path = str(template_path).replace(os.sep, '/')

            template = environment.get_template( template_path )

            page_html = ""
            try:
                template_filename = Path(template_path).stem
                expected_object_id = f"{project_abbr}.{template_filename}"
                material_object = self.app_context.get_app_data_store().find_object(expected_object_id)
                if material_object is None:
                    # default "just render" the page
                    page_html = template.render(project=project_data)
                else:
                    # additionally assign object data if pagename corresponds to object with id.
                    page_html = template.render(project=project_data, object=material_object)

            except Exception as e:
                msg = f"Failed to render page html for page template {page.name} for project {project_abbr}. Original error: {e}"
                logging.error(msg)
                page_html = ApplicationErrorHtmlBuilder.build_general_error_html(msg)
            finally:
                output_path = Path(output_dir).joinpath(page.stem + '.html')
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(page_html)
                    logging.info(f"Successfully wrote {page.name} to {output_path}")
