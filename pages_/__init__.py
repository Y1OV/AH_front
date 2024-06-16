from collections import namedtuple

from lct.videos_from_archive import main as videos_from_archive
from lct.main import main as main


Page = namedtuple("Page", "title method")

pages: dict[str, Page] = {
    'Главная': Page(title="История распознаваний", method=main),
    'archive': Page(title="Разпознать из архива", method=videos_from_archive),

}
