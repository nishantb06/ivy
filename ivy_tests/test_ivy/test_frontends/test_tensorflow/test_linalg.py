# global
import numpy as np
from hypothesis import strategies as st
import sys

# local
import ivy_tests.test_ivy.helpers as helpers
from ivy_tests.test_ivy.helpers import handle_frontend_test
from ivy_tests.test_ivy.test_functional.test_core.test_linalg import (
    _get_dtype_value1_value2_axis_for_tensordot,
)


@st.composite
def _get_dtype_and_matrix(draw):
    arbitrary_dims = draw(helpers.get_shape(max_dim_size=5))
    random_size = draw(st.integers(min_value=1, max_value=4))
    shape = (*arbitrary_dims, random_size, random_size)
    return draw(
        helpers.dtype_and_values(
            available_dtypes=helpers.get_dtypes("float"),
            shape=shape,
            min_value=-10,
            max_value=10,
        )
    )


@handle_frontend_test(
    fn_tree="tensorflow.linalg.det",
    dtype_and_input=_get_dtype_and_matrix(),
)
def test_tensorflow_det(
    *,
    dtype_and_input,
    num_positional_args,
    as_variable,
    native_array,
    frontend,
    fn_tree,
    on_device,
):
    input_dtype, x = dtype_and_input
    helpers.test_frontend_function(
        input_dtypes=input_dtype,
        native_array_flags=native_array,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        input=x[0],
    )


@handle_frontend_test(
    fn_tree="tensorflow.linalg.eigh",
    dtype_and_input=_get_dtype_and_matrix(),
)
def test_tensorflow_eigh(
    *,
    dtype_and_input,
    num_positional_args,
    as_variable,
    native_array,
    frontend,
    fn_tree,
    on_device,
):
    input_dtype, x = dtype_and_input
    helpers.test_frontend_function(
        input_dtypes=input_dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        tensor=x[0],
    )


@handle_frontend_test(
    fn_tree="tensorflow.linalg.eigvalsh",
    dtype_and_input=_get_dtype_and_matrix(),
)
def test_tensorflow_eigvalsh(
    *,
    dtype_and_input,
    num_positional_args,
    as_variable,
    native_array,
    frontend,
    fn_tree,
    on_device,
):
    input_dtype, x = dtype_and_input
    helpers.test_frontend_function(
        input_dtypes=input_dtype,
        native_array_flags=native_array,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        tensor=x[0],
    )


@handle_frontend_test(
    fn_tree="tensorflow.linalg.matrix_rank",
    dtype_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        min_num_dims=2,
        min_value=-1e05,
        max_value=1e05,
    ),
    tolr=st.floats(allow_nan=False, allow_infinity=False) | st.just(None),
)
def test_matrix_rank(
    *,
    dtype_x,
    tolr,
    num_positional_args,
    native_array,
    as_variable,
    frontend,
    fn_tree,
    on_device,
):
    input_dtype, x = dtype_x
    helpers.test_frontend_function(
        input_dtypes=input_dtype,
        native_array_flags=native_array,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        atol=1.0,
        a=x[0],
        tol=tolr,
    )


@st.composite
def _solve_get_dtype_and_data(draw):
    batch = draw(st.integers(min_value=1, max_value=5))
    random_size = draw(st.integers(min_value=2, max_value=4))
    input_dtype = draw(
        st.shared(
            st.sampled_from(draw(helpers.get_dtypes("float"))),
            key="shared_dtype",
        )
    )
    shape = (random_size, random_size)
    tmp = []
    for i in range(batch):
        tmp.append(
            draw(
                helpers.array_values(
                    dtype=input_dtype,
                    shape=shape,
                    min_value=-10,
                    max_value=10,
                ).filter(
                    lambda x: np.linalg.cond(x.tolist()) < 1 / sys.float_info.epsilon
                )
            )
        )
    shape = (batch, random_size, draw(st.integers(min_value=2, max_value=4)))
    input_dtype2, x = draw(
        helpers.dtype_and_values(
            available_dtypes=draw(helpers.get_dtypes("float")),
            shape=shape,
            min_value=-10,
            max_value=10,
        )
    )

    return [[input_dtype] * batch, input_dtype2[0]], [tmp, x[0]]


# solve
@handle_frontend_test(
    fn_tree="tensorflow.linalg.solve",
    dtype_and_x=_solve_get_dtype_and_data(),
)
def test_tensorflow_solve(
    *,
    dtype_and_x,
    num_positional_args,
    as_variable,
    native_array,
    frontend,
    fn_tree,
    on_device,
):
    input_dtypes, xs = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=[input_dtypes[0][0], input_dtypes[1]],
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-3,
        atol=1e-3,
        matrix=xs[0],
        rhs=xs[1],
    )


# logdet
@st.composite
def _get_hermitian_pos_def_matrix(draw):
    # batch_shape, random_size, shared
    input_dtype = draw(
        st.shared(
            st.sampled_from(draw(helpers.get_dtypes("float"))),
            key="shared_dtype",
        )
    )
    shared_size = draw(
        st.shared(helpers.ints(min_value=2, max_value=4), key="shared_size")
    )
    gen = draw(
        helpers.array_values(
            dtype=input_dtype,
            shape=tuple([shared_size, shared_size]),
            min_value=2,
            max_value=5,
        ).filter(lambda x: np.linalg.cond(x.tolist()) < 1 / sys.float_info.epsilon)
    )
    hpd = np.matmul(np.matrix(gen).getH(), np.matrix(gen)) + np.identity(gen.shape[0])
    return [input_dtype], hpd


@handle_frontend_test(
    fn_tree="tensorflow.linalg.logdet",
    dtype_and_x=_get_hermitian_pos_def_matrix(),
)
def test_tensorflow_logdet(
    *,
    dtype_and_x,
    with_out,
    num_positional_args,
    as_variable,
    native_array,
    frontend,
    fn_tree,
    on_device,
):
    dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        matrix=x,
    )


# slogdet
@handle_frontend_test(
    fn_tree="tensorflow.linalg.slogdet",
    dtype_and_x=_get_dtype_and_matrix(),
)
def test_tensorflow_slogdet(
    *,
    dtype_and_x,
    num_positional_args,
    as_variable,
    native_array,
    frontend,
    fn_tree,
    on_device,
):
    input_dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=input_dtype,
        native_array_flags=native_array,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        input=x[0],
    )


# cholesky_solve
@st.composite
def _get_cholesky_matrix(draw):
    # batch_shape, random_size, shared
    input_dtype = draw(
        st.shared(
            st.sampled_from(draw(helpers.get_dtypes("float"))),
            key="shared_dtype",
        )
    )
    shared_size = draw(
        st.shared(helpers.ints(min_value=2, max_value=4), key="shared_size")
    )
    gen = draw(
        helpers.array_values(
            dtype=input_dtype,
            shape=tuple([shared_size, shared_size]),
            min_value=2,
            max_value=5,
        ).filter(lambda x: np.linalg.cond(x.tolist()) < 1 / sys.float_info.epsilon)
    )
    spd = np.matmul(gen.T, gen) + np.identity(gen.shape[0])
    spd_chol = np.linalg.cholesky(spd)
    return input_dtype, spd_chol


@st.composite
def _get_second_matrix(draw):
    # batch_shape, shared, random_size
    input_dtype = draw(
        st.shared(
            st.sampled_from(draw(helpers.get_dtypes("float"))),
            key="shared_dtype",
        )
    )
    shared_size = draw(
        st.shared(helpers.ints(min_value=2, max_value=4), key="shared_size")
    )
    return input_dtype, draw(
        helpers.array_values(
            dtype=input_dtype, shape=tuple([shared_size, 1]), min_value=2, max_value=5
        )
    )


@handle_frontend_test(
    fn_tree="tensorflow.linalg.cholesky_solve",
    x=_get_cholesky_matrix(),
    y=_get_second_matrix(),
)
def test_tensorflow_cholesky_solve(
    *,
    x,
    y,
    num_positional_args,
    as_variable,
    native_array,
    frontend,
    fn_tree,
    on_device,
):
    input_dtype1, x1 = x
    input_dtype2, x2 = y
    helpers.test_frontend_function(
        input_dtypes=[input_dtype1, input_dtype2],
        native_array_flags=native_array,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-3,
        atol=1e-3,
        chol=x1,
        rhs=x2,
    )


# pinv
@handle_frontend_test(
    fn_tree="tensorflow.linalg.pinv",
    dtype_and_input=_get_dtype_and_matrix(),
)
def test_tensorflow_pinv(
    *,
    dtype_and_input,
    num_positional_args,
    as_variable,
    native_array,
    frontend,
    fn_tree,
    on_device,
):
    input_dtype, x = dtype_and_input
    helpers.test_frontend_function(
        input_dtypes=input_dtype,
        native_array_flags=native_array,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        a=x[0],
        rcond=1e-15,
    )


# tensordot
@handle_frontend_test(
    fn_tree="tensorflow.linalg.tensordot",
    dtype_x_y_axes=_get_dtype_value1_value2_axis_for_tensordot(
        available_dtypes=helpers.get_dtypes("numeric"),
    ),
)
def test_tensorflow_tensordot(
    *,
    dtype_x_y_axes,
    num_positional_args,
    as_variable,
    native_array,
    frontend,
    fn_tree,
    on_device,
):
    (
        dtype,
        x,
        y,
        axes,
    ) = dtype_x_y_axes
    helpers.test_frontend_function(
        input_dtypes=dtype,
        native_array_flags=native_array,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        a=x,
        b=y,
        axes=axes,
    )


# norm
@handle_frontend_test(
    fn_tree="tensorflow.linalg.norm",
    dtype_values_axis=helpers.dtype_values_axis(
        available_dtypes=helpers.get_dtypes("valid"),
        min_num_dims=3,
        max_num_dims=5,
        min_dim_size=1,
        max_dim_size=4,
        min_axis=-3,
        max_axis=2,
    ),
    ord=st.sampled_from([1, 2, np.inf]),
    keepdims=st.booleans(),
)
def test_tensorflow_norm(
    *,
    dtype_values_axis,
    ord,
    keepdims,
    num_positional_args,
    as_variable,
    native_array,
    frontend,
    fn_tree,
    on_device,
):
    input_dtype, x, axis = dtype_values_axis
    helpers.test_frontend_function(
        input_dtypes=input_dtype,
        native_array_flags=native_array,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        tensor=x[0],
        ord=ord,
        axis=axis,
        keepdims=keepdims,
    )


# normalize
@handle_frontend_test(
    fn_tree="tensorflow.linalg.normalize",
    dtype_values_axis=helpers.dtype_values_axis(
        available_dtypes=helpers.get_dtypes("valid"),
        min_num_dims=3,
        max_num_dims=5,
        min_dim_size=1,
        max_dim_size=4,
        min_axis=-3,
        max_axis=2,
    ),
    ord=st.sampled_from([1, 2, np.inf]),
)
def test_tensorflow_normalize(
    *,
    dtype_values_axis,
    ord,
    num_positional_args,
    as_variable,
    native_array,
    frontend,
    fn_tree,
    on_device,
):
    input_dtype, x, axis = dtype_values_axis
    helpers.test_frontend_function(
        input_dtypes=input_dtype,
        native_array_flags=native_array,
        as_variable_flags=as_variable,
        with_out=False,
        with_inplace=False,
        num_positional_args=num_positional_args,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        tensor=x[0],
        ord=ord,
        axis=axis,
    )


# l2_normalize
@handle_frontend_test(
    fn_tree="tensorflow.linalg.l2_normalize",
    dtype_values_axis=helpers.dtype_values_axis(
        available_dtypes=helpers.get_dtypes("valid"),
        min_num_dims=3,
        max_num_dims=5,
        min_dim_size=1,
        max_dim_size=4,
        min_axis=-3,
        max_axis=2,
    ),
)
def test_tensorflow_l2_normalize(
    *,
    dtype_values_axis,
    num_positional_args,
    as_variable,
    native_array,
    frontend,
    fn_tree,
    on_device,
):
    input_dtype, x, axis = dtype_values_axis
    helpers.test_frontend_function(
        input_dtypes=input_dtype,
        native_array_flags=native_array,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        x=x[0],
        axis=axis,
    )


# trace
@handle_frontend_test(
    fn_tree="tensorflow.linalg.trace",
    dtype_and_input=_get_dtype_and_matrix(),
    num_positional_args=helpers.num_positional_args(
        fn_name="ivy.functional.frontends.tensorflow.linalg.trace"
    ),
)
def test_tensorflow_trace(
    dtype_and_input,
    as_variable,
    num_positional_args,
    native_array,
    frontend,
    fn_tree,
):
    input_dtype, x = dtype_and_input
    helpers.test_frontend_function(
        input_dtypes=input_dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        x=x[0],
    )


# matrix_transpose
@handle_frontend_test(
    fn_tree="tensorflow.linalg.matrix_transpose",
    dtype_and_input=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("valid"),
        min_num_dims=2,
    ),
)
def test_tensorflow_matrix_transpose(
    dtype_and_input,
    as_variable,
    num_positional_args,
    native_array,
    frontend,
    fn_tree,
):
    input_dtype, x = dtype_and_input
    helpers.test_frontend_function(
        input_dtypes=input_dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        a=x[0],
    )
