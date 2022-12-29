# __metaclass__ = type

import json
import os
import subprocess
import tempfile

from ansible.errors import AnsibleAction, AnsibleActionFail
from ansible.module_utils.common.process import get_bin_path
from ansible.plugins.action import ActionBase


class ActionModule(ActionBase):
    TRANSFERS_FILES = True
    ARGUMENT_SPEC = {
        "image": {"type": "str", "required": True},
        "destination": {"type": "str", "required": True},
    }

    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)
        _, task_args = self.validate_argument_spec(self.ARGUMENT_SPEC)

        image_name = task_args["image"]
        destination = task_args["destination"]

        try:
            tmpdir = self._make_tmp_path()

            with tempfile.TemporaryDirectory(prefix="oci-image-unpack") as tmpdir:
                oci_image_path = os.path.join(tmpdir, "image")
                oci_bundle_path = os.path.join(tmpdir, "bundle")

                oci_image_fetch(image_name, oci_image_path)
                oci_image_unpack(oci_image_path, oci_bundle_path)
                rootfs = oci_bundle_get_rootfs(oci_bundle_path)

                # Rootfs must end with a trailing slash because we want rsync
                # to copy the content of rootfs, not the rootfs itself.
                if not rootfs.endswith(os.path.sep):
                    rootfs = rootfs + os.path.sep

                result.update(self._run_synchronize_action(task_vars, src=rootfs, dest=destination))
        except AnsibleAction as e:
            result.update(e.result)
        return result

    def _run_synchronize_action(self, task_vars, **synchronize_kwargs):
        """Delegate synchronization to the synchronize action (3rd party)."""

        copy_task = self._task.copy()
        copy_task.args = synchronize_kwargs
        copy_action = self._shared_loader_obj.action_loader.get(
            "ansible.posix.synchronize",
            task=copy_task,
            connection=self._connection,
            play_context=self._play_context,
            loader=self._loader,
            templar=self._templar,
            shared_loader_obj=self._shared_loader_obj,
        )
        return copy_action.run(task_vars=task_vars)


def oci_image_fetch(image_name: str, destination: str) -> None:
    """Downloads a given OCI image to local disk."""

    try:
        skopeo = get_bin_path("skopeo")
    except ValueError as exc:
        raise AnsibleActionFail(str(exc))

    process = subprocess.run(
        [
            skopeo,
            "copy",
            image_name,
            f"oci:{ destination }:latest",
        ],
        capture_output=True,
    )

    if process.returncode != 0:
        raise AnsibleActionFail(
            f"failed to download the container image: { image_name }",
            result={
                "stdout": process.stdout,
                "stderr": process.stderr,
            },
        )


def oci_image_unpack(image_path: str, destination: str) -> None:
    """Unpacks OCI image to limage.tarocal disk."""

    try:
        umoci = get_bin_path("umoci")
    except ValueError as exc:
        raise AnsibleActionFail(str(exc))

    process = subprocess.run(
        [
            umoci,
            "unpack",
            "--rootless",
            "--image",
            image_path,
            destination,
        ],
        capture_output=True,
    )

    if process.returncode != 0:
        raise AnsibleActionFail(
            f"failed to extract the container image: { image_path }",
            result={
                "stdout": process.stdout,
                "stderr": process.stderr,
            },
        )


def oci_bundle_get_rootfs(bundle_path: str) -> str:
    """Returns a path to rootfs fot a given OCI bundle."""

    with open(os.path.join(bundle_path, "config.json")) as fobj:
        config = json.loads(fobj.read())
    return os.path.join(bundle_path, config["root"]["path"])
