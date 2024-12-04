# Author: Sebastian Schiller-Stoff
# Description: File allows to define certain function to manipulate the SSR process
# e.g. to filter out certain digital-objects or to load digital-objects from a different source


#
#
# # Use cases
# # - Add objects to the list
# def modify_object_data(digital_objects):
#     """
#     Custom function allows to modify digital objects data in memory.
#     :param digital_objects: list of digital objects
#     :return: list of digital objects
#     """
#
#     filtered = []
#
#     for digital_object in  digital_objects:
#         # print(digital_object.db)
#         if digital_object.db["baseMetadata"]["title"] == 'Alexei Jopich':
#             filtered.append(digital_object)
#             pass
#         else:
#             pass
#
#
#     return filtered
#
#
# # Completely rewrite what objects are being loaded
# def load_digital_objects():
#     """
#     Custom function allows to build digital objects in memory.
#     :return: list of digital objects
#     """
#
#     return []

#
# def extend_object_view_fn(digital_objects, load_template_fn, render_view_fn):
#     """
#
#     :return:
#     """
#
#     # must be called first to load the template (which template? belongs to the operation?)
#     load_template_fn("object.jinja")
#
#     # define correspondent location per object
#     # TODO add logic that only certain objects are being rendered (like of type 'event')
#     for digital_object in digital_objects:
#         # defines where the html file will be saved (and so the REST-PATH)
#         # mapping to the relative path
#         # TODO ids should be constructed in a certain way.
#         render_view_fn(digital_object, f"different/{digital_object.db['id']}")


