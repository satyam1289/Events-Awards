
# Python 3.13 polyfill for removed 'cgi' module
# Newspaper4k and some other libs still look for it.

def parse_header(line):
    import email.message
    m = email.message.Message()
    m['content-type'] = line
    return m.get_content_type(), m.get_params()

# Keep only what's absolutely needed for common libs
class FieldStorage:
    pass
