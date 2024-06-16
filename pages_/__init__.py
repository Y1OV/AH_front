from collections import namedtuple

from .videos_from_archive import main as videos_from_archive
from .main import main as main


Page = namedtuple("Page", "title method")

pages: dict[str, Page] = {
    'Главная': Page(title="Главная", method=main),
    'archive': Page(title="Разпознать из архива", method=videos_from_archive),

}
