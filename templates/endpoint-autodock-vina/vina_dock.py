from __future__ import annotations


def dock(
    receptor: str,
    ligand: str,
    output: str,
    center: list[float],
    size: list[float],
    exhaustiveness: int,
    n_poses: int,
    cpu: int,
    seed: int,
) -> list[list[float]]:
    """Run one docking. Called in a child process: the Vina binding holds the GIL while it docks."""
    from vina import Vina

    vina = Vina(sf_name="vina", cpu=cpu, seed=seed, verbosity=1)
    vina.set_receptor(receptor)
    vina.set_ligand_from_file(ligand)
    vina.compute_vina_maps(center=center, box_size=size)
    vina.dock(exhaustiveness=exhaustiveness, n_poses=n_poses)
    vina.write_poses(output, n_poses=n_poses, overwrite=True)
    return vina.energies(n_poses=n_poses).tolist()
