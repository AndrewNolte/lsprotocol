#include <rapidjson/document.h>
namespace lsp {

using LSPObject = rapidjson::GenericObject<true, rapidjson::Value>;

using LSPArray = rapidjson::GenericArray<true, rapidjson::Value>;

using LSPAny = rapidjson::GenericValue<rapidjson::UTF8<>, rapidjson::Value>;

} // namespace lsp