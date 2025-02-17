
from copy import deepcopy
from pathlib import Path

import numpy as np
from monty.serialization import loadfn
from pymatgen.core import Element
from pymatgen.core import Structure
from pymatgen.analysis.local_env import NearNeighbors

from submodels import Converter
from models.layers.atom_env import StructureGraphFixedRadius

MODULE_DIR = Path(__file__).parent.absolute()



class CrystalPro(StructureGraphFixedRadius):
    """
    Convert a crystal into a graph with z as atomic feature and distance as bond feature
    one can optionally include state features
    """

    def __init__(
        self,
        nn_strategy = "MinimumDistanceNNAll",
        atom_converter = None,
        bond_converter = None,
        cutoff: float = 5.0,
    ):

        self.cutoff = cutoff
        super().__init__(
            nn_strategy=nn_strategy,
            atom_converter=atom_converter,
            bond_converter=bond_converter,
            cutoff=self.cutoff
        )


class _AtomEmbeddingMap(Converter):


    def __init__(self, embedding_dict = None):
        self.embedding_dict = embedding_dict

    def convert(self, atoms: list) -> np.ndarray:
        """
        Convert atom {symbol: fraction} list to numeric features
        """
        features = []
        for atom in atoms:
            emb = 0
            for k, v in atom.items():
                emb += np.array(self.embedding_dict[k]) * v
            features.append(emb)
        return np.array(features).reshape((len(atoms), -1))


class CrystalGraphDisordered(StructureGraphFixedRadius):


    def __init__(
        self,
        nn_strategy = "MinimumDistanceNNAll",
        atom_converter = _AtomEmbeddingMap(),
        bond_converter = None,
        cutoff: float = 5.0,
    ):
        """
        Convert the structure into crystal graph
        Args:
            nn_strategy (str): NearNeighbor strategy
            atom_converter (Converter): atom features converter
            bond_converter (Converter): bond features converter
            cutoff (float): cutoff radius
        """
        self.cutoff = cutoff
        super().__init__(
            nn_strategy=nn_strategy, atom_converter=atom_converter, bond_converter=bond_converter, cutoff=self.cutoff
        )

    @staticmethod
    def get_atom_features(structure):
        """
        For a structure return the list of dictionary for the site occupancy
        for example, Fe0.5Ni0.5 site will be returned as {"Fe": 0.5, "Ni": 0.5}

        Args:
            structure (Structure): pymatgen Structure with potential site disorder

        Returns:
            a list of site fraction description
        """
        return [i.species.as_dict() for i in structure.sites]
