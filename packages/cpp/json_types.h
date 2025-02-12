#include <rapidjson/document.h>


using LSPObject = rapidjson::GenericObject<true, rapidjson::Value>;

using LSPArray = rapidjson::GenericArray<true, rapidjson::Value>;

using LSPAny = rapidjson::GenericValue<rapidjson::UTF8<>, rapidjson::Value>;