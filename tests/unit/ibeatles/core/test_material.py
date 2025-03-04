#!/usr/bin/env python
"""Unit tests for ibeatles.core.material module."""

import pytest
import numpy as np
from ibeatles.core.config import Material, CustomMaterial
from ibeatles.core.material import get_bragg_edges, get_initial_bragg_edge_lambda


@pytest.fixture
def fe_material_config():
    """Fixture for Iron material config."""
    return Material(element="Fe")


@pytest.fixture
def custom_material_config():
    """Fixture for custom material config."""
    return Material(
        custom_material=CustomMaterial(
            name="Custom Alloy",
            lattice=3.52,
            crystal_structure="BCC",
            hkl_lambda_pairs={(1, 1, 0): 2.8664, (2, 0, 0): 2.0267},
        )
    )


class TestGetBraggEdges:
    def test_valid_element(self, fe_material_config):
        """Test getting Bragg edges for a valid element (Fe)."""
        result = get_bragg_edges(fe_material_config)

        assert result["name"] == "Fe"
        assert result["crystal_structure"] == {"Fe": "BCC"}
        assert isinstance(result["lattice"], float)
        assert isinstance(result["bragg_edges"], (list, np.ndarray))
        assert len(result["bragg_edges"]) > 0
        # Known first Bragg edge for Fe
        assert pytest.approx(result["bragg_edges"][0], rel=1e-4) == 4.0537

    def test_custom_material(self, custom_material_config):
        """Test getting Bragg edges for a custom material."""
        result = get_bragg_edges(custom_material_config)

        assert result["name"] == "Custom Alloy"
        assert result["crystal_structure"] == "BCC"
        assert result["lattice"] == 3.52
        assert isinstance(result["bragg_edges"], (list, np.ndarray))
        assert len(result["bragg_edges"]) > 0

    def test_invalid_element(self):
        """Test error handling for invalid element."""
        invalid_material = Material(element="InvalidElement")
        with pytest.raises(ValueError, match="Error getting Bragg edges"):
            get_bragg_edges(invalid_material)

    def test_invalid_custom_material(self):
        """Test error handling for invalid custom material."""
        invalid_custom = Material(
            custom_material=CustomMaterial(
                name="Invalid",
                lattice=-1.0,  # Invalid lattice parameter
                crystal_structure="INVALID",
                hkl_lambda_pairs={(1, 1, 0): 2.8664},
            )
        )
        with pytest.raises(ValueError, match="Error creating custom material"):
            get_bragg_edges(invalid_custom)

    def test_no_material(self):
        """Test error when no material is specified."""
        # Pydantics is catching this error
        with pytest.raises(ValueError, match="validation error"):
            get_bragg_edges(Material())


class TestGetInitialBraggEdgeLambda:
    def test_valid_range(self, fe_material_config):
        """Test getting initial Bragg edge within valid range."""
        lambda_range = (2.0, 5.0)
        result = get_initial_bragg_edge_lambda(fe_material_config, lambda_range)

        assert lambda_range[0] <= result <= lambda_range[1]
        assert isinstance(result, float)

    def test_multiple_edges_in_range(self, fe_material_config):
        """Test that middle edge is selected when multiple edges in range."""
        # Wide range that should include multiple edges
        lambda_range = (1.0, 5.0)
        result = get_initial_bragg_edge_lambda(fe_material_config, lambda_range)

        edges = get_bragg_edges(fe_material_config)["bragg_edges"]
        valid_edges = [
            edge for edge in edges if lambda_range[0] <= edge <= lambda_range[1]
        ]

        # Should choose middle edge
        expected = valid_edges[len(valid_edges) // 2]
        assert result == expected

    def test_no_edges_in_range(self, fe_material_config):
        """Test error when no edges in specified range."""
        lambda_range = (0.1, 0.2)  # Range too low for Fe
        with pytest.raises(ValueError, match="No Bragg edges found in range"):
            get_initial_bragg_edge_lambda(fe_material_config, lambda_range)

    def test_custom_material_edge(self, custom_material_config):
        """Test getting edge for custom material."""
        lambda_range = (1.0, 4.0)
        result = get_initial_bragg_edge_lambda(custom_material_config, lambda_range)

        assert lambda_range[0] <= result <= lambda_range[1]
        assert isinstance(result, float)

    def test_invalid_range(self, fe_material_config):
        """Test error handling for invalid range specification."""
        # Inverted range
        with pytest.raises(ValueError):
            get_initial_bragg_edge_lambda(fe_material_config, (5.0, 2.0))


if __name__ == "__main__":
    pytest.main(["-v", __file__])
