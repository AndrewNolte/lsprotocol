
#pragma once
#include <filesystem>
#include <iostream>
#include <string>

class URI {
    /// File URIs- assumes file:// prefix

  public:
    using ReflectionType = std::string;

    URI() = default;

    URI(const char* _str) : underlying_(_str) {}

    URI(const std::string& _str) : underlying_(_str) {}

    ~URI() = default;

    // Equality operator (needed for unordered_map)
    bool operator==(const URI& other) const {
        return underlying_ == other.underlying_;
    }

    /// Necessary for the serialization to work.
    ReflectionType reflection() const { return underlying_; }

    /// Expresses the underlying URI as a string.
    std::string str() const { return reflection(); }

    std::string_view getPath() const {
        if (underlying_.size() < 7) {
            return {};
        }
        return std::string_view(underlying_).substr(7);
    }


    static URI fromFile(const std::filesystem::path& file) {
        return URI("file://" + file.string());
    }

    friend std::ostream& operator<<(std::ostream& os, const URI& uri) {
        os << uri.str();
        return os;
    }

  private:
    /// The underlying string
    std::string underlying_;
};

namespace std {
template <> struct hash<URI> {
    std::size_t operator()(const URI& uri) const noexcept {
        return std::hash<std::string>{}(uri.str());
    }
};
} // namespace std