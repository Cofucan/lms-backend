from enum import Enum


class Stack(str, Enum):
    """Enum list of all the stacks
    
    BE, FE, DESIGN, PM, CLOUD, and DS
    """
    BE = "backend"
    FE = "frontend"
    DESIGN = "design"
    PM = "product management"
    CLOUD = "cloud engineering"
    DS = "data science"

class Track(str, Enum):
    """Enum list of all the tracks in different stacks

    Backend:
        BE_NODE, BE_PYTHON, BE_PHP, BE_GO
    Frontend:
        FE_VUE, FE_REACT, FE_VANILLA
    Design:
        PRODUCT_DESIGN, UIUX_DESIGN
    """
    BE_NODE = "nodejs"
    BE_PYTHON = "python"
    BE_PHP = "php"
    BE_GO = "golang"
    FE_VUE = "vuejs"
    FE_REACT = "reactjs"
    FE_VANILLA = "vanillajs"
    PRODUCT_DESIGN = "product design"
    UIUX_DESIGN = "ui/ux design"


class Proficiency(str, Enum):
    """Enum list of all the proficency levels

    BEGINNER, INTERMEDIATE, ADVANCED
    """
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"