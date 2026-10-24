module;
#include <onnxruntime_cxx_api.h>
#include <cpu_provider_factory.h>
#include <provider_options.h>
#include <onnxruntime_lite_custom_op.h>
#include <core/providers/custom_op_context.h>
#include <core/providers/resource.h>

export module mcpplibs.mwrap.onnxruntime;

export import mcpplibs.mwrap.onnxruntime.macros;
#include "exports.inc"
