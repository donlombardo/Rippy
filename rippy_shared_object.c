#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <stdbool.h>

#define CHUNK_SIZE (1024 * 1024)  // 1MB chunks

// Function to calculate AccurateRip v1 and v2 checksums
static void generate_checksums(const uint32_t *data_buffer, size_t buffer_size, size_t track_number, size_t total_tracks_count, uint32_t *checksum_1, uint32_t *checksum_2) {
    uint32_t high_part = 0;
    uint32_t low_part = 0;
    uint32_t start_offset = 0;
    size_t total_samples = buffer_size / sizeof(uint32_t);
    uint32_t end_offset = total_samples;
    const size_t sector = 2352;
    uint32_t count_multiplier = 1;
    size_t index;

    if (track_number == 1)
        start_offset += (sector * 5) / sizeof(uint32_t);
    if (track_number == total_tracks_count)
        end_offset -= (sector * 5) / sizeof(uint32_t);

    for (index = 0; index < total_samples; index++) {
        if (count_multiplier >= start_offset && count_multiplier <= end_offset) {
            uint64_t temp_product = (uint64_t)data_buffer[index] * (uint64_t)count_multiplier;
            high_part += (uint32_t)(temp_product >> 32);
            low_part += (uint32_t)(temp_product);
        }
        count_multiplier++;
    }

    *checksum_1 = low_part;
    *checksum_2 = low_part + high_part;
}

// Python wrapper function
static PyObject *compute_checksums(PyObject *self, PyObject *args) {
    PyObject *py_bytes;
    Py_ssize_t buffer_size;
    unsigned int track_id, total_tracks;
    uint32_t checksum_1, checksum_2;
    uint32_t *data_buffer;

    if (!PyArg_ParseTuple(args, "y#II", &py_bytes, &buffer_size, &track_id, &total_tracks)) {
        return NULL;
    }

    if (buffer_size % sizeof(uint32_t) != 0) {
        PyErr_SetString(PyExc_ValueError, "Invalid PCM buffer size");
        return NULL;
    }

    data_buffer = (uint32_t *)py_bytes;
    generate_checksums(data_buffer, buffer_size, track_id, total_tracks, &checksum_1, &checksum_2);
    return Py_BuildValue("II", checksum_1, checksum_2);
}

// Function to compare byte arrays and store differing bytes in a dictionary
static PyObject* find_differing(PyObject *self, PyObject *args) {
    PyObject *filenames;
    if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &filenames)) {
        return NULL;
    }

    Py_ssize_t num_files = PyList_Size(filenames);
    if (num_files == 0) {
        PyErr_SetString(PyExc_ValueError, "No input files provided!");
        return NULL;
    }

    FILE *file_handles[num_files];
    struct stat file_stats[num_files];
    memset(file_handles, 0, sizeof(file_handles));

    for (Py_ssize_t i = 0; i < num_files; i++) {
        PyObject *py_filename = PyList_GetItem(filenames, i);
        if (!PyUnicode_Check(py_filename)) {
            PyErr_SetString(PyExc_TypeError, "Filenames must be strings.");
            return NULL;
        }
        const char *filename = PyUnicode_AsUTF8(py_filename);

        if (stat(filename, &file_stats[i]) != 0) {
            PyErr_Format(PyExc_FileNotFoundError, "File not found: %s", filename);
            return NULL;
        }
        if (file_stats[i].st_size == 0) {
            PyErr_Format(PyExc_ValueError, "File is empty: %s", filename);
            return NULL;
        }

        file_handles[i] = fopen(filename, "rb");
        if (!file_handles[i]) {
            PyErr_Format(PyExc_IOError, "Could not open file: %s", filename);
            return NULL;
        }
    }

    size_t min_file_size = file_stats[0].st_size;
    for (Py_ssize_t i = 1; i < num_files; i++) {
        if ((size_t)file_stats[i].st_size != min_file_size) {
            PyErr_SetString(PyExc_ValueError, "Files must have the same size.");
            return NULL;
        }
    }

    size_t chunk_size = CHUNK_SIZE / num_files;
    unsigned char *buffers[num_files];
    for (Py_ssize_t i = 0; i < num_files; i++) {
        buffers[i] = (unsigned char *)malloc(chunk_size);
        if (!buffers[i]) {
            PyErr_NoMemory();
            return NULL;
        }
    }

    PyObject *diff_dict = PyDict_New();
    size_t position = 0;

    while (1) {
        size_t bytes_read = fread(buffers[0], 1, chunk_size, file_handles[0]);
        if (bytes_read == 0) break;

        for (Py_ssize_t i = 1; i < num_files; i++) {
            fread(buffers[i], 1, bytes_read, file_handles[i]);
        }

        for (size_t i = 0; i < bytes_read; i++) {
            int differing = 0;
            for (Py_ssize_t j = 1; j < num_files; j++) {
                if (buffers[j][i] != buffers[0][i]) {
                    differing = 1;
                    break;
                }
            }
            if (differing) {
                PyObject *byte_list = PyList_New(num_files);
                for (Py_ssize_t j = 0; j < num_files; j++) {
                    PyList_SetItem(byte_list, j, PyLong_FromLong(buffers[j][i]));
                }
                PyDict_SetItem(diff_dict, PyLong_FromSize_t(position + i), byte_list);
                Py_DECREF(byte_list);
            }
        }
        position += bytes_read;
    }

    for (Py_ssize_t i = 0; i < num_files; i++) {
        fclose(file_handles[i]);
        free(buffers[i]);
    }
    return diff_dict;
}

// Function to compare byte buffers and find differing positions
static PyObject *compare_buffers(PyObject *self, PyObject *args) {
    PyObject *list_obj;
    Py_ssize_t min_len, num_chunks;

    if (!PyArg_ParseTuple(args, "Ol", &list_obj, &min_len)) {
        return NULL;
    }

    num_chunks = PyList_Size(list_obj);
    if (num_chunks < 2) {
        PyErr_SetString(PyExc_ValueError, "Need at least two buffers.");
        return NULL;
    }

    uint8_t **buffers = (uint8_t **)malloc(num_chunks * sizeof(uint8_t *));
    if (!buffers) {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate buffer array.");
        return NULL;
    }

    for (Py_ssize_t i = 0; i < num_chunks; i++) {
        PyObject *bytes_obj = PyList_GetItem(list_obj, i);
        if (!PyBytes_Check(bytes_obj)) {
            free(buffers);
            PyErr_SetString(PyExc_TypeError, "List elements must be bytes.");
            return NULL;
        }
        buffers[i] = (uint8_t *)PyBytes_AsString(bytes_obj);
    }

    bool *diff_flags = (bool *)calloc(min_len, sizeof(bool));
    if (!diff_flags) {
        free(buffers);
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate diff_flags.");
        return NULL;
    }

    for (Py_ssize_t i = 0; i < min_len; i++) {
        uint8_t ref_byte = buffers[0][i];
        for (Py_ssize_t j = 1; j < num_chunks; j++) {
            if (buffers[j][i] != ref_byte) {
                diff_flags[i] = true;
                break;
            }
        }
    }

    PyObject *diff_dict = PyDict_New();
    for (Py_ssize_t i = 0; i < min_len; i++) {
        if (diff_flags[i]) {
            PyObject *values_list = PyList_New(num_chunks);
            for (Py_ssize_t j = 0; j < num_chunks; j++) {
                PyList_SetItem(values_list, j, PyLong_FromLong(buffers[j][i]));
            }
            PyDict_SetItem(diff_dict, PyLong_FromSsize_t(i), values_list);
            Py_DECREF(values_list);
        }
    }

    free(buffers);
    free(diff_flags);
    return diff_dict;
}

// Define module methods
static PyMethodDef ModuleMethods[] = {
    {"compute", compute_checksums, METH_VARARGS, "Compute AccurateRip v1 and v2 checksums"},
    {"find_differing", find_differing, METH_VARARGS, "Find differing bytes across multiple files"},
    {"compare_buffers", compare_buffers, METH_VARARGS, "Find differing bytes across multiple buffers"},
    {NULL, NULL, 0, NULL}
};

// Define module
static struct PyModuleDef ModuleDefinition = {
    PyModuleDef_HEAD_INIT,
    "rippy_shared_object",
    NULL,
    -1,
    ModuleMethods
};

// Module initialization
PyMODINIT_FUNC PyInit_rippy_shared_object(void) {
    return PyModule_Create(&ModuleDefinition);
}

