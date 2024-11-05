#!/usr/bin/env python
"""Materials model for fitting."""

from typing import Union, Dict, Tuple, List
from neutronbraggedge.braggedge import BraggEdge
from ibeatles.core.config import Material


def get_bragg_edges(
    material_config: Material,
) -> Dict[str, Union[str, float, List[float]]]:
    """
    Get Bragg edge information based on material configuration.

    Parameters
    ----------
    material_config : Material
        Material configuration from IBeatlesUserConfig

    Returns
    -------
    Dict[str, Union[str, float, List[float]]]
        Dictionary containing:
        - 'name': Material name
        - 'crystal_structure': Crystal structure
        - 'lattice': Lattice parameter
        - 'bragg_edges': List of Bragg edge values

    Examples
    --------
    >>> material_config = Material(element='Fe')
    >>> edges = get_bragg_edges(material_config)
    >>> print(edges['bragg_edges'][0])  # First Bragg edge
    4.0537

    >>> material_config = Material(
    ...     custom_material=CustomMaterial(
    ...         name='Custom',
    ...         lattice=3.52,
    ...         crystal_structure='BCC',
    ...         hkl_lambda_pairs={(1,1,0): 2.8664, (2,0,0): 2.0267}
    ...     )
    ... )
    >>> edges = get_bragg_edges(material_config)
    """
    if material_config.element is not None:
        # Use predefined element
        # TODO: the number of edges should be computed based on the maximum HKL range
        try:
            material = BraggEdge(
                material=material_config.element,
                number_of_bragg_edges=10,
            )
            return {
                "name": material_config.element,
                "crystal_structure": material.metadata["crystal_structure"],
                "lattice": material.metadata["lattice"].get(material_config.element),
                "bragg_edges": material.bragg_edges[material_config.element],
            }
        except Exception as e:
            raise ValueError(
                f"Error getting Bragg edges for {material_config.element}: {str(e)}"
            )

    elif material_config.custom_material is not None:
        # Use custom material
        custom = material_config.custom_material

        # Create material definition for neutronbraggedge
        new_material = [
            {
                "name": custom.name,
                "lattice": custom.lattice,
                "crystal_structure": custom.crystal_structure,
            }
        ]

        try:
            material = BraggEdge(
                material=custom.name,
                new_material=new_material,
                number_of_bragg_edges=len(custom.hkl_lambda_pairs),
            )

            return {
                "name": custom.name,
                "crystal_structure": custom.crystal_structure,
                "lattice": custom.lattice,
                "bragg_edges": material.bragg_edges[custom.name],
            }

        except Exception as e:
            raise ValueError(f"Error creating custom material {custom.name}: {str(e)}")

    else:
        raise ValueError("No material specified in configuration")


def get_initial_bragg_edge_lambda(
    material_config: Material, lambda_range: Tuple[float, float]
) -> float:
    """
    Get initial guess for Bragg edge wavelength within specified range.

    Parameters
    ----------
    material_config : Material
        Material configuration from IBeatlesUserConfig
    lambda_range : Tuple[float, float]
        (min, max) wavelength range to consider

    Returns
    -------
    float
        Initial guess for Bragg edge wavelength
    """
    edges = get_bragg_edges(material_config)
    bragg_edges = edges["bragg_edges"]

    # Find edges within range
    valid_edges = [
        edge for edge in bragg_edges if lambda_range[0] <= edge <= lambda_range[1]
    ]

    if not valid_edges:
        raise ValueError(f"No Bragg edges found in range {lambda_range}")

    # Use middle edge in range as initial guess
    return valid_edges[len(valid_edges) // 2]
