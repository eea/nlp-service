# from datetime import datetime
# from typing import Dict, Tuple
#
# import haystack.nodes.base

# original_dispatch_run = haystack.nodes.base.BaseComponent._dispatch_run
#
#
# def timed_dispatch_run(self, **kwargs) -> Tuple[Dict, str]:
#     before = datetime.now()
#
#     print(f"{self.name} node start at {before}")
#     ret = original_dispatch_run(self, **kwargs)
#     after = datetime.now()
#     print(f"{self.name} node end at {before}")
#     delta = after - before
#     print(f"{self.name} node response in {delta.total_seconds()} seconds")
#     print("---------")
#     (res, val) = ret
#     if type(res) is dict:
#         res["elapsed"] = res.get("elapsed", [])
#         res["elapsed"].append(
#             {self.name: {"start": before, "end": after, "delta": delta.total_seconds()}}
#         )
#     return ret
#
#
# print("PATCH BASECOMPONENT")
# haystack.nodes.base.BaseComponent._dispatch_run = timed_dispatch_run
