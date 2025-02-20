__title__ = "DVD"
__doc__ = """Classic DVD screensaver animation for Rhino.

A nostalgic entertainment feature that recreates the 
bouncing DVD logo animation within Rhino viewport."""


from EnneadTab import LOG, ERROR_HANDLE, JOKE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def dvd():
    JOKE.prank_dvd()

if __name__ == "__main__":
    dvd()