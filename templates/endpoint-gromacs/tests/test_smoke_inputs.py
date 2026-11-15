from __future__ import annotations

import itertools
import math

from app import default_inputs


def mdp_values(text: str) -> dict[str, str]:
    pairs = (line.split("=", 1) for line in text.splitlines() if "=" in line)
    return {key.strip().replace("_", "-"): value.strip() for key, value in pairs}


def test_argon_smoke_inputs_are_physically_consistent():
    inputs = default_inputs(10000, 0.001, 120.0, 17)
    mdp = mdp_values(inputs["mdp"])
    top = inputs["top"].splitlines()
    gro = inputs["gro"].splitlines()

    # sigma/epsilon parameters require combination rule 2 (or 3), not C6/C12 rule 1.
    assert top[top.index("[ defaults ]") + 1].split()[1] == "2"
    assert "Ar 18 39.948 0.0 A 0.3405 0.996" in top

    atoms = int(gro[1])
    assert len(gro) == atoms + 3
    assert top[-1].split() == ["ARG", str(atoms)]
    box = [float(value) for value in gro[-1].split()]
    assert len(set(box)) == 1
    assert box[0] / 2 > max(float(mdp["rvdw"]), float(mdp["rcoulomb"])) + 0.2

    coordinates = [tuple(float(line[20 + 8 * axis : 28 + 8 * axis]) for axis in range(3)) for line in gro[2:-1]]
    closest = min(
        math.dist(a, [b[axis] - box[axis] * round((b[axis] - a[axis]) / box[axis]) for axis in range(3)])
        for a, b in itertools.combinations(coordinates, 2)
    )
    assert closest > 0.3405 * 2 ** (1 / 6) * 1.1  # no overlap: well beyond the LJ minimum

    density = atoms / box[0] ** 3
    assert 15 < density < 22  # atoms/nm^3, liquid argon is ~17.5 near 120 K

    assert mdp["tcoupl"] == "v-rescale"
    assert float(mdp["ref-t"]) == float(mdp["gen-temp"]) == 120.0
