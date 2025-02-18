import numpy as np
import pytest

from ndsl.comm._boundary_utils import _shift_boundary_slice, get_boundary_slice
from ndsl.constants import (
    EAST,
    NORTH,
    SOUTH,
    WEST,
    X_DIM,
    X_INTERFACE_DIM,
    Y_DIM,
    Z_DIM,
)
from ndsl.quantity import Quantity


def boundary_data(quantity, boundary_type, n_points, interior=True):
    boundary_slice = get_boundary_slice(
        quantity.dims,
        quantity.origin,
        quantity.extent,
        quantity.data.shape,
        boundary_type,
        n_points,
        interior,
    )
    return quantity.data[tuple(boundary_slice)]


@pytest.mark.cpu_only
def test_boundary_data_1_by_1_array_1_halo():
    quantity = Quantity(
        np.random.randn(3, 3),
        dims=[Y_DIM, X_DIM],
        units="m",
        origin=(1, 1),
        extent=(1, 1),
    )
    for side in (
        WEST,
        EAST,
        NORTH,
        SOUTH,
    ):
        assert (
            boundary_data(quantity, side, n_points=1, interior=True)
            == quantity.data[1, 1]
        )

    assert (
        boundary_data(quantity, NORTH, n_points=1, interior=False)
        == quantity.data[2, 1]
    )
    assert (
        boundary_data(quantity, SOUTH, n_points=1, interior=False)
        == quantity.data[0, 1]
    )
    assert (
        boundary_data(quantity, WEST, n_points=1, interior=False) == quantity.data[1, 0]
    )
    assert (
        boundary_data(quantity, EAST, n_points=1, interior=False) == quantity.data[1, 2]
    )


def test_boundary_data_3d_array_1_halo_z_offset_origin(numpy):
    quantity = Quantity(
        numpy.random.randn(2, 3, 3),
        dims=[Z_DIM, Y_DIM, X_DIM],
        units="m",
        origin=(1, 1, 1),
        extent=(1, 1, 1),
    )
    for side in (
        WEST,
        EAST,
        NORTH,
        SOUTH,
    ):
        quantity.np.testing.assert_array_equal(
            boundary_data(quantity, side, n_points=1, interior=True),
            quantity.data[1, 1, 1],
        )

    quantity.np.testing.assert_array_equal(
        boundary_data(quantity, NORTH, n_points=1, interior=False),
        quantity.data[1, 2, 1],
    )
    quantity.np.testing.assert_array_equal(
        boundary_data(quantity, SOUTH, n_points=1, interior=False),
        quantity.data[1, 0, 1],
    )
    quantity.np.testing.assert_array_equal(
        boundary_data(quantity, WEST, n_points=1, interior=False),
        quantity.data[1, 1, 0],
    )
    quantity.np.testing.assert_array_equal(
        boundary_data(quantity, EAST, n_points=1, interior=False),
        quantity.data[1, 1, 2],
    )


@pytest.mark.cpu_only
def test_boundary_data_2_by_2_array_2_halo():
    quantity = Quantity(
        np.random.randn(6, 6),
        dims=[Y_DIM, X_DIM],
        units="m",
        origin=(2, 2),
        extent=(2, 2),
    )
    for side in (
        WEST,
        EAST,
        NORTH,
        SOUTH,
    ):
        np.testing.assert_array_equal(
            boundary_data(quantity, side, n_points=2, interior=True),
            quantity.data[2:4, 2:4],
        )

    quantity.np.testing.assert_array_equal(
        boundary_data(quantity, NORTH, n_points=1, interior=True),
        quantity.data[3:4, 2:4],
    )
    quantity.np.testing.assert_array_equal(
        boundary_data(quantity, NORTH, n_points=1, interior=False),
        quantity.data[4:5, 2:4],
    )
    quantity.np.testing.assert_array_equal(
        boundary_data(quantity, NORTH, n_points=2, interior=False),
        quantity.data[4:6, 2:4],
    )
    quantity.np.testing.assert_array_equal(
        boundary_data(quantity, SOUTH, n_points=1, interior=True),
        quantity.data[2:3, 2:4],
    )
    quantity.np.testing.assert_array_equal(
        boundary_data(quantity, SOUTH, n_points=1, interior=False),
        quantity.data[1:2, 2:4],
    )
    quantity.np.testing.assert_array_equal(
        boundary_data(quantity, SOUTH, n_points=2, interior=False),
        quantity.data[0:2, 2:4],
    )
    quantity.np.testing.assert_array_equal(
        boundary_data(quantity, WEST, n_points=2, interior=False),
        quantity.data[2:4, 0:2],
    )
    quantity.np.testing.assert_array_equal(
        boundary_data(quantity, WEST, n_points=1, interior=True),
        quantity.data[2:4, 2:3],
    )
    quantity.np.testing.assert_array_equal(
        boundary_data(quantity, WEST, n_points=1, interior=False),
        quantity.data[2:4, 1:2],
    )
    quantity.np.testing.assert_array_equal(
        boundary_data(quantity, EAST, n_points=1, interior=False),
        quantity.data[2:4, 4:5],
    )
    quantity.np.testing.assert_array_equal(
        boundary_data(quantity, EAST, n_points=2, interior=False),
        quantity.data[2:4, 4:6],
    )
    quantity.np.testing.assert_array_equal(
        boundary_data(quantity, EAST, n_points=1, interior=True),
        quantity.data[2:4, 3:4],
    )


@pytest.mark.parametrize(
    "dim, origin, extent, boundary_type, slice_object, reference",
    [
        pytest.param(
            X_DIM,
            1,
            3,
            WEST,
            slice(None, None),
            slice(1, 4),
            id="none_is_changed",
        ),
        pytest.param(
            Y_DIM,
            1,
            3,
            WEST,
            slice(None, None),
            slice(1, 4),
            id="perpendicular_none_is_changed",
        ),
        pytest.param(
            X_DIM,
            1,
            3,
            WEST,
            slice(0, 1),
            slice(1, 2),
            id="shift_to_start",
        ),
        pytest.param(
            X_DIM,
            1,
            3,
            WEST,
            slice(0, 2),
            slice(1, 3),
            id="shift_larger_to_start",
        ),
        pytest.param(
            X_DIM,
            1,
            3,
            EAST,
            slice(0, 1),
            slice(4, 5),
            id="shift_to_end",
        ),
        pytest.param(
            X_INTERFACE_DIM,
            1,
            3,
            WEST,
            slice(0, 1),
            slice(1, 2),
            id="shift_interface_to_start",
        ),
        pytest.param(
            X_INTERFACE_DIM,
            1,
            3,
            EAST,
            slice(0, 1),
            slice(4, 5),
            id="shift_interface_to_end",
        ),
        pytest.param(
            Y_DIM,
            2,
            4,
            SOUTH,
            slice(0, 1),
            slice(2, 3),
            id="shift_y_to_start",
        ),
        pytest.param(
            Y_DIM,
            2,
            4,
            NORTH,
            slice(0, 1),
            slice(6, 7),
            id="shift_y_to_end",
        ),
    ],
)
@pytest.mark.cpu_only
def test_shift_boundary_slice(
    dim, origin, extent, boundary_type, slice_object, reference
):
    result = _shift_boundary_slice(dim, origin, extent, boundary_type, slice_object)
    assert result == reference
