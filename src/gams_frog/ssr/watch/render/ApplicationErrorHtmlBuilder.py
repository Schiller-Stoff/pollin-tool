

class ApplicationErrorHtmlBuilder:
    """
    Manages HTML error messages to show the gams_frog tool user
    if something went wrong during templating

    """

    _GENERAL_ERROR_TEMPLATE = "<html><body style='padding: 1em 5em; font-family: MONOSPACE; font-size:1.2em; line-height:1.5em;'><div style='max-width: 75%'><h1 style='color: red'>GAMS_FROG ERROR</h1> <p>Occurred at static site generation (template-rendering)</p><p>{}</p></div></body></html>"

    @staticmethod
    def build_general_error_html(msg):
        return ApplicationErrorHtmlBuilder._GENERAL_ERROR_TEMPLATE.format(msg)