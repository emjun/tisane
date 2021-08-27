import json
import os
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)


class GUIStrings:
    def __init__(self):
        self.data = {}
        dir = os.path.dirname(os.path.abspath(__file__))
        stringsPath = os.path.join(dir, "strings.json")
        if os.path.exists(stringsPath):
            with open(stringsPath, "r") as f:
                self.data = json.loads(f.read())
                pass
            pass
        else:
            log.error("Could not find strings.json file in dir {}".format(dir))
            exit(1)
            pass
        pass

    def _safeAccess(self, *args):
        assert len(args) > 0, "Must specify at least one argument."
        for i in range(len(args)):
            arg = args[i]
            if i == 0:
                assert arg in self.data, "Could not find {} in {}".format(
                    arg, self.data
                )
                pass
            else:
                level = self.data[args[0]]
                if i > 1:
                    for j in range(1, i):
                        level = level[args[j]]
                        pass
                    pass
                assert arg in level, "Could not find {} for ({}) in {}".format(
                    arg, ",".join(args[0:i]), level
                )
                pass
            pass
        result = self.data[args[0]]
        if len(args) > 1:
            for i in range(1, len(args)):
                result = result[args[i]]
                pass
            pass
        return result

    def __call__(self, *args):
        return self._safeAccess(*args)

    def access(self, *args):
        return self._safeAccess(*args)

    def getTitle(self, topic: str, elementType: str):
        return self._safeAccess(topic, "titles", elementType)

    def getPageTitle(self, topic: str):
        # assert topic in self.data, "Key {} does not exist in {}".format(topic, self.data)

        return self.getTitle(topic, "page")

    def getNoPageTitle(self, topic: str):
        return self.getTitle(topic, "page-no")

    def getTabTitle(self, topic: str):
        return self.getTitle(topic, "tab")

    def getMainEffectsPageTitle(self):
        return self.getPageTitle("main-effects")

    def getInteractionEffectsPageTitle(self):
        return self.getPageTitle("interaction-effects")

    def getFamilyLinksPageTitle(self):
        return self.getPageTitle("family-link-functions")

    def getRandomEffectsPageTitle(self):
        return self.getPageTitle("random-effects")

    def getMainEffectsNoPageTitle(self):
        return self.getNoPageTitle("main-effects")

    def getInteractionEffectsNoPageTitle(self):
        return self.getNoPageTitle("interaction-effects")

    def getRandomEffectsNoPageTitle(self):
        return self.getNoPageTitle("random-effects")

    def getMainEffectsTabTitle(self):
        return self.getTabTitle("main-effects")

    def getInteractionEffectsTabTitle(self):
        return self.getTabTitle("interaction-effects")

    def getRandomEffectsTabTitle(self):
        return self.getTabTitle("random-effects")

    def getFamilyLinksTabTitle(self):
        return self.getTabTitle("family-link-functions")
