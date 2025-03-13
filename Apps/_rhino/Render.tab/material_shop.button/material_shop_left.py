__title__ = "MaterialShop"
__doc__ = "Your gateway to a treasure trove of high-quality materials! Opens AmbientCG, a fantastic resource offering hundreds of free PBR materials perfect for architectural visualization. Quickly find textures, HDRIs, and 3D models to elevate your renderings without spending a penny."


from EnneadTab import ERROR_HANDLE, LOG
import webbrowser

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def material_shop():
    webbrowser.open("https://ambientcg.com/")

    
if __name__ == "__main__":
    material_shop()
