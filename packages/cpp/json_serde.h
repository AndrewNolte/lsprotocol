#include <string>
#include <tuple>

#include "rapidjson/document.h"

template <typename T> struct Reflectable;

#define REFLECTABLE(...)                                                       \
    template <> struct Reflectable<std::decay_t<decltype(*this)>> {            \
        using Type = std::decay_t<decltype(*this)>;                            \
        static constexpr auto get_members() {                                  \
            return std::make_tuple(__VA_ARGS__);                               \
        }                                                                      \
    };

#define MEMBER(name) std::make_pair(#name, &Type::name)

template <typename T>
void to_json(rapidjson::Value& v,
             const T& obj,
             rapidjson::Document::AllocatorType& allocator) {
    v.SetObject();
    auto members = Reflectable<T>::get_members();
    std::apply(
            [&](auto&&... args) {
                ((serialize_member(v, obj, args.first, args.second, allocator)),
                 ...);
            },
            members);
}

template <typename T, typename MemberPtr>
void serialize_member(rapidjson::Value& v,
                      const T& obj,
                      const char* name,
                      MemberPtr ptr,
                      rapidjson::Document::AllocatorType& allocator) {
    rapidjson::Value key(name, allocator);
    using MemberType = decltype(obj.*ptr);
    rapidjson::Value value;

    if constexpr (std::is_same_v<MemberType, int>) {
        value.SetInt(obj.*ptr);
    } else if constexpr (std::is_same_v<MemberType, std::string>) {
        value.SetString((obj.*ptr).c_str(), allocator);
    }
    // Handle other types as needed

    v.AddMember(key, value, allocator);
}

template <typename T> void from_json(const rapidjson::Value& v, T& obj) {
    auto members = Reflectable<T>::get_members();
    std::apply(
            [&](auto&&... args) {
                ((deserialize_member(v, obj, args.first, args.second)), ...);
            },
            members);
}

template <typename T, typename MemberPtr>
void deserialize_member(const rapidjson::Value& v,
                        T& obj,
                        const char* name,
                        MemberPtr ptr) {
    if (v.HasMember(name)) {
        const auto& value = v[name];
        using MemberType = decltype(obj.*ptr);

        if constexpr (std::is_same_v<MemberType, int> && value.IsInt()) {
            obj.*ptr = value.GetInt();
        } else if constexpr (std::is_same_v<MemberType, std::string> &&
                             value.IsString()) {
            obj.*ptr = value.GetString();
        }
        // Handle other types as needed
    }
}

/// Begin Generated Code

struct InitializeParams {
    int processId;
    std::string rootUri;

    REFLECTABLE(MEMBER(processId), MEMBER(rootUri))
};
