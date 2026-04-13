import logging
import os
from pathlib import Path
import jinja2
from jinja2 import Environment, Template

from gams_frog.ssr.init.ApplicationContext import ApplicationContext
from gams_frog.ssr.watch.render.ApplicationErrorHtmlBuilder import ApplicationErrorHtmlBuilder
from gams_frog.ssr.watch.utils.RenderUtils import RenderUtils


class DigitalObjectViewRenderer:
    """
    Translates given Digital Objects into HTML files
    """

    app_context: ApplicationContext
    """
    The application context
    """

    environment: Environment
    """
    Jinja2 environment
    """

    custom_template: Template
    """
    Jinja2 template that can be loaded and used to render custom views
    """


    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context
        # jinja2 environment setup in constructor
        self.environment = jinja2.Environment(loader=jinja2.FileSystemLoader(self.app_context.get_config().project_src_view_template_dir))

    def render(self):
        """
        Renders the views for object based data
        :param data: list of DigitalObjects
        :param project_metadata: metadata of the GAMS project
        :return:
        """

        output_dir = self.app_context.get_config().project_public_dir
        # make sure that the object output directory exists
        os.makedirs(Path(output_dir).joinpath("objects"), exist_ok=True)

        # digital objects
        data = self.app_context.get_app_data_store().get_objects()
        # metadata about the project
        project_metadata = self.app_context.get_app_data_store().project_data
        project_abbr = self.app_context.get_config().project

        for digital_object in data:
            object_id = digital_object["id"]
            object_html = ""
            object_template_name = 'object.j2'

            obj_template_target_output_path = Path(output_dir).joinpath("objects").joinpath(object_id)
            obj_template_relative_path_to_root = RenderUtils.calc_relative_path(output_dir, obj_template_target_output_path)

            try:
                object_template = self.environment.get_template(object_template_name)
                render_context = {
                    "context": {
                        'object': digital_object,
                        'project': project_metadata,
                        'env': self.app_context.get_config().ENV.to_dict(),
                        '_template_name': object_template_name.replace(".j2", ""),
                        '_template_file_name': object_template_name,
                        '_root_path': obj_template_relative_path_to_root
                    }
                }
                object_html = object_template.render(render_context)
            except Exception as e:
                msg = f"Failed to render template {object_template_name} for object {digital_object['id']}. Original error: {e}"
                logging.error(msg)
                object_html = ApplicationErrorHtmlBuilder.build_general_error_html(msg)
            finally:
                # writing the object html to file in any case
                os.makedirs(obj_template_target_output_path, exist_ok=True)
                with open(obj_template_target_output_path.joinpath("index.html"), "w", encoding="utf-8") as f:
                    f.write(object_html)
                    logging.info(f"Successfully wrote object {object_id} to file")

        # rendering of project home page
        project_html = ""
        project_template_name = "project.j2"

        project_template_target_output_path = Path(output_dir)
        project_template_relative_path_to_root = RenderUtils.calc_relative_path(output_dir, project_template_target_output_path)

        try:
            project_template = self.environment.get_template(project_template_name)
            render_context = {
                "context": {
                    'project': project_metadata,
                    'env': self.app_context.get_config().ENV.to_dict(),
                    '_template_name': project_template_name.replace(".j2", ""),
                    '_template_file_name': project_template_name,
                    '_root_path': project_template_relative_path_to_root
                }
            }
            project_html = project_template.render(render_context)
        except Exception as e:
            msg = f"Failed to render template {project_template_name} for project {project_abbr}. Original error: {e}"
            logging.error(msg)
            project_html = ApplicationErrorHtmlBuilder.build_general_error_html(msg)
        finally:
            with open(project_template_target_output_path.joinpath("index.html"), "w", encoding="utf-8") as f:
                f.write(project_html)
                logging.info(f"Successfully wrote project home page {project_abbr}")

        # Rendering of object overview page

        object_list_html = ""
        object_list_template_name = 'object-list.j2'

        object_list_template_target_output_path = Path(output_dir).joinpath("objects")
        object_list_template_relative_path_to_root = (RenderUtils
                                                      .calc_relative_path(output_dir,object_list_template_target_output_path))

        try:
            object_list_template = self.environment.get_template(object_list_template_name)
            render_context = {
                "context": {
                    'objects': data,
                    'project': project_metadata,
                    'env': self.app_context.get_config().ENV.to_dict(),
                    '_template_name': object_list_template_name.replace(".j2", ""),
                    '_template_file_name': object_list_template_name,
                    '_root_path': object_list_template_relative_path_to_root
                }
            }
            object_list_html = object_list_template.render(render_context)
        except Exception as e:
            msg = f"Failed to render template {object_list_template_name} for object-list for project {project_abbr}. Original error: {e}"
            logging.error(msg)
            object_list_html = ApplicationErrorHtmlBuilder.build_general_error_html(msg)
        finally:
            with open(object_list_template_target_output_path.joinpath("index.html"), "w", encoding="utf-8") as f:
                f.write(object_list_html)

    def activate_custom_template(self, template_name):
        """
        Loads a custom jinja template and stores it as class variable
        :return:
        """

        self.custom_template = self.environment.get_template(template_name)
        logging.info(f"Successfully loaded and activated custom template {template_name}")

    def render_view(self, digital_object, relative_path):
        """
        Renders a view for a given digital object and stores it in the defined directory
        :param digital_object: the digital object
        :param relative_path: the relative path where the view should be stored (as directory - mapped to index.html)
        :return:
        """
        if self.custom_template is None:
            msg = f"Cannot find current custom template for object: {str(digital_object)} for the relative path: {relative_path}"
            logging.error(msg)
            raise ValueError(msg)

        output_dir = self.app_context.get_config().project_public_dir

        project_metadata = self.app_context.get_app_data_store().project_data
        content = self.custom_template.render(object=digital_object, project=project_metadata)

        # TODO add some error checking for the relative_path?
        relative_path = Path(relative_path)
        # ensure that the path exists?
        os.makedirs(Path(output_dir).joinpath(relative_path), exist_ok=True)

        output_file = Path(output_dir).joinpath(relative_path).joinpath("index.html")

        # store file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
            logging.info(f"Successfully wrote object {digital_object['id']} to file at {output_file}")