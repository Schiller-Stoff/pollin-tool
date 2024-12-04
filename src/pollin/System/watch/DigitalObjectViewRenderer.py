import logging
import os
from pathlib import Path
import jinja2
from jinja2 import Environment, Template

from pollin.System.load.DigitalObjectService import DigitalObjectService
from pollin.System.init.ApplicationContext import ApplicationContext

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

        # digital objects
        data = self.app_context.get_app_data_store().get_objects()
        # metadata about the project
        project_metadata = self.app_context.get_app_data_store().project_data

        for digital_object in data:

            object_template = self.environment.get_template('object.jinja')
            content = object_template.render(object=digital_object, project=project_metadata)
            object_id = digital_object.db["id"]

            cur_object_folder = Path(output_dir).joinpath("objects").joinpath(object_id)
            os.makedirs(cur_object_folder, exist_ok=True)

            with open(cur_object_folder.joinpath("index.html"), "w", encoding="utf-8") as f:
                f.write(content)
                logging.info(f"Successfully wrote object {object_id} to file")


        # rendering of project home page
        home_template = self.environment.get_template('project.jinja')
        home_content = home_template.render(project=project_metadata)
        with open(Path(output_dir).joinpath("index.html"), "w", encoding="utf-8") as f:
            f.write(home_content)

        # TODO think about list of all objects?
        object_list_template = self.environment.get_template('object-list.jinja')
        object_list_content = object_list_template.render(objects=data, project=project_metadata)
        with open(Path(output_dir).joinpath("objects").joinpath("index.html"), "w", encoding="utf-8") as f:
            f.write(object_list_content)


        ####
        #
        # Possible extension rendering process for digital objects?
        #

        # import function from app script
        # TODO handle hardcoded function name? (extend_object_view_fn)
        extend_object_view_fn = self.app_context.get_app_script_importer().get_function("extend_object_view_fn")
        if extend_object_view_fn is None:
            logging.info("No extend_object_view_fn function found. Using default rendering process.")
        else:
            logging.info("Found extend_object_view_fn function")
            # experimental custom process
            extend_object_view_fn(data, self.activate_custom_template, self.render_view)


        ####
        # create object_index_json
        DigitalObjectService.aggregate_index_json(
            self.app_context.get_config().project_public_dir,
            self.app_context.get_app_data_store().get_objects()
        )

        # create object_index_geo.json
        DigitalObjectService.aggregate_geo_json(
            self.app_context.get_config().project_public_dir,
            self.app_context.get_app_data_store().get_objects()
        )


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
            msg = f"Cannot find current custom template for object: {str(digital_object.db)} for the relative path: {relative_path}"
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
            logging.info(f"Successfully wrote object {digital_object.db['id']} to file at {output_file}")