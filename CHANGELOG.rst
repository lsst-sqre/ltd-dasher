##########
Change log
##########

0.1.4 (2019-10-6)
=================

- Added a Kustomize manifest deploying LTD Dasher that replaces the original set of manifests in the previous ``/kubernetes/`` directory.
  One key change is that this deployment relies on secrets from the LTD Keeper deployment, and thus should be deployed into the same namespace as LTD Keeper.
  This new Kustomize-base deployment is being used for the Roundtable project: see https://github.com/lsst-sqre/roundtable/tree/master/deployments/lsst-the-docs.

0.1.3 (2018-07-11)
==================

- Fixed a bug when an LTD Keeper Edition had a ``tracked_refs`` field with a value of ``None`` (because the Edition does not use the ``git_refs`` tracking mode`).
  First, the GitHub link does not appear if ``tracked_refs`` is not available.
  Second, version heuristics are now computed against the ``slug``.
