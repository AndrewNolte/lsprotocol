
#pragma once

#include <rfl/json.hpp>
#include <string>
namespace lsp {

using LSPObject = rfl::Object<std::string>;

using LSPArray = std::vector<rfl::Generic>;

using LSPAny = rfl::Generic;

} // namespace lsp