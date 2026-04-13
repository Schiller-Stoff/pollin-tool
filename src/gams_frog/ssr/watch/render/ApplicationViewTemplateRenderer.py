import logging
import os.path
from pathlib import Path
import jinja2
from gams_frog.ssr.init.ApplicationContext import ApplicationContext
from gams_frog.ssr.watch.render.ApplicationErrorHtmlBuilder import ApplicationErrorHtmlBuilder
from gams_frog.ssr.watch.utils.RenderUtils import RenderUtils

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


    def delete_output_file(self, src_path: str):
        """
        Deletes the output file for the correspondent source file
        :param src_path path to the source file
        """

        output_dir = self.app_context.get_config().project_public_dir
        output_path = Path(output_dir).joinpath(Path(src_path).stem + '.html')

        if os.path.exists(output_path):
            os.remove(output_path)
            logging.info(f"Succesfully deleted output file at {output_path}")
        else:
            msg = f"Failed to delete output render-file at: {output_path} for src file: {src_path}. This might lead to unexpected behaviors of the pollin tool"
            logging.warning(msg)


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

            template_relative_path_to_root = RenderUtils.calc_relative_path(self.app_context.get_config().project_public_dir,
                                                                                    output_dir)
            page_html = ""
            try:
                template = environment.get_template( template_path )
                template_filename = Path(template_path).stem
                # check if jinja template starts with "memo."
                if template_filename.startswith(f"{project_abbr}."):
                    expected_object_id = template_filename
                    object_to_bind = self.app_context.get_app_data_store().find_object(expected_object_id)
                    if object_to_bind:
                        render_context = {
                            "context": {
                                'project': project_data,
                                'env': self.app_context.get_config().ENV.to_dict(),
                                '_template_name': template_filename.replace(".j2", ""),
                                '_template_file_name': template_filename,
                                '_root_path': template_relative_path_to_root
                            }
                        }
                        page_html = template.render(render_context)
                    else:
                        msg = f"Cannot find object {expected_object_id} to bind to jinja template with name {template_filename}"
                        logging.error(msg)
                        raise LookupError(msg)
                else:
                    # just render page if not following template name convention.
                    render_context = {
                        "context": {
                            'project': project_data,
                            'env': self.app_context.get_config().ENV.to_dict(),
                            '_template_name': template_path.replace(".j2", ""),
                            '_template_file_name': template_path,
                            '_root_path': template_relative_path_to_root
                        }
                    }
                    page_html = template.render(render_context)

            except Exception as e:
                msg = f"Failed to render page html for page template {page.name} for project {project_abbr}. At template_path: {template_path} Original error: {e}"
                logging.error(msg)
                page_html = ApplicationErrorHtmlBuilder.build_general_error_html(msg)
            finally:
                output_path = Path(output_dir).joinpath(page.stem + '.html')
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(page_html)
                    logging.info(f"Successfully wrote {page.name} to {output_path}")
