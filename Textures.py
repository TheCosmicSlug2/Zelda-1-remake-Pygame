from Settings import *


def convert_to_pygame_texture(texture_path: str, dims: tuple) -> pg.surface:
    """
    On prend le chemin de l'image
    On la convertit en objet pygame
    On dessine cet objet sur une surface pour pouvoir "blitter" directement sur écran
    (Impossible de blitter une image pygame)
    On retourne la surface
    """

    img = pg.image.load(texture_path).convert_alpha()
    img = pg.transform.scale(img, dims)
    surface = pg.Surface(dims, pg.SRCALPHA)
    surface.blit(img, (0, 0))
    return surface


def load_textures(dic_path: dict, texture_size: list, cell_dims: tuple) -> dict:

    """
    Ce code a vraiment besoin d'une explication...

    :param dic_path: Format : "idx : nom_texture"
    :param texture_size: Format : "[[nom_texture, ..., (texture_size_x, texture_size_y), ...]
    :param cell_dims: La largeur d'une texture de décor (PAS DU JOUEUR HEIN), La hauteur d'une texture de décor
    :return:
    """

    print("\n[TextureLoader] : Les textures suivantes ont été mises à la taille par défaut : \n")

    # 1er élément de ce dictionnaire utilisé pour dessiner le cache du décor
    dic_textures = {"dims": cell_dims}

    # Pour pas avoir à réécrire toutes les extensions
    dir_textures_path = "ressources/textures/"
    texture_ext = ".png"

    # Pour chaque idx_de_texture, nom_de_la_texture
    for texture_ID, texture_name in dic_path.items():
        # Pour chaque idx_de_liste de la liste texture_size
        found = False

        dic_textures[texture_ID] = convert_to_pygame_texture(
            dir_textures_path + texture_name + texture_ext,
            dic_textures["dims"]
        )
        for texture_family_idx in range(len(texture_size)):
            # Si l'idx est 0 : dims = cellsizex, cellsizey (dimensions possiblement non constantes)
            # Donc là en gros c'est un safeguard je crois
            # -> toutes les textures sont mises par défaut aux dims de base

            # Sinon : dimensions sont prédéfinies (celles du joueur ou des ennemis)
            # et dcp c'est juste si on les trouve autre part qu'elles sont mises à différentes sizes
            if texture_name in texture_size[texture_family_idx]:
                dims = texture_size[texture_family_idx][-1]
                dic_textures[texture_ID] = convert_to_pygame_texture(dir_textures_path + texture_name + texture_ext,
                                                                     dims)
                found = True

        if found == False:
            print(f"\"{texture_name}\"", end="\n")
    
    print("\nTextures crées\n")
    return dic_textures