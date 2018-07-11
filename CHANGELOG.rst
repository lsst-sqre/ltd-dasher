##########
Change log
##########

0.1.3 (2018-07-11)
==================

- Fixed a bug when an LTD Keeper Edition had a ``tracked_refs`` field with a value of ``None`` (because the Edition does not use the ``git_refs`` tracking mode`).
  First, the GitHub link does not appear if ``tracked_refs`` is not available.
  Second, version heuristics are now computed against the ``slug``.
