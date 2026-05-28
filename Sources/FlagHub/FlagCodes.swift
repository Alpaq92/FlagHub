//
//  FlagCodes.swift
//  FlagHub
//
//  Country / region code enumeration and a `Flag.all` accessor.
//

import Foundation

extension Flag {

    /// Every country / region code that FlagHub ships an asset for.
    ///
    /// The list is mostly ISO 3166-1 alpha-2, with a few additions:
    /// `EU` (European Union), `WW` (default / unknown world flag),
    /// `GB-ENG`, `GB-NIR`, `GB-SCT`, `GB-WLS`, `GB-ZET` (UK subdivisions),
    /// `LGBT` (Pride), and `US-CA` (California).
    public static let supportedCountryCodes: [String] = [
        "AD", "AE", "AF", "AG", "AI", "AL", "AM", "AO", "AR", "AS",
        "AT", "AU", "AW", "AX", "AZ", "BA", "BB", "BD", "BE", "BF",
        "BG", "BH", "BI", "BJ", "BL", "BM", "BN", "BO", "BR", "BS",
        "BT", "BV", "BW", "BY", "BZ", "CA", "CC", "CD", "CF", "CG",
        "CH", "CI", "CK", "CL", "CM", "CN", "CO", "CR", "CU", "CV",
        "CW", "CX", "CY", "CZ", "DE", "DJ", "DK", "DM", "DO", "DZ",
        "EC", "EE", "EG", "ER", "ES", "ET", "EU", "FI", "FJ", "FK",
        "FM", "FO", "FR", "GA", "GB", "GB-ENG", "GB-NIR", "GB-SCT", "GB-WLS", "GB-ZET",
        "GD", "GE", "GF", "GG", "GH", "GI", "GL", "GM", "GN", "GP",
        "GQ", "GR", "GS", "GT", "GU", "GW", "GY", "HK", "HM", "HN",
        "HR", "HT", "HU", "ID", "IE", "IL", "IM", "IN", "IO", "IQ",
        "IR", "IS", "IT", "JE", "JM", "JO", "JP", "KE", "KG", "KH",
        "KI", "KM", "KN", "KP", "KR", "KW", "KY", "KZ", "LA", "LB",
        "LC", "LGBT", "LI", "LK", "LR", "LS", "LT", "LU", "LV", "LY",
        "MA", "MC", "MD", "ME", "MF", "MG", "MH", "MK", "ML", "MM",
        "MN", "MO", "MP", "MQ", "MR", "MS", "MT", "MU", "MV", "MW",
        "MX", "MY", "MZ", "NA", "NC", "NE", "NF", "NG", "NI", "NL",
        "NO", "NP", "NR", "NU", "NZ", "OM", "PA", "PE", "PF", "PG",
        "PH", "PK", "PL", "PM", "PN", "PR", "PS", "PT", "PW", "PY",
        "QA", "RE", "RO", "RS", "RU", "RW", "SA", "SB", "SC", "SD",
        "SE", "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO",
        "SR", "SS", "ST", "SV", "SX", "SY", "SZ", "TC", "TD", "TF",
        "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO", "TR", "TT",
        "TV", "TW", "TZ", "UA", "UG", "UM", "US", "US-CA", "UY", "UZ",
        "VA", "VC", "VE", "VG", "VI", "VN", "VU", "WF", "WS", "WW",
        "XK", "YE", "YT", "ZA", "ZM", "ZW"
    ]

    /// Every flag FlagHub ships, materialised. Returned in the same
    /// alphabetical order as ``supportedCountryCodes``.
    ///
    /// The list is computed lazily on each access; pin it to a local
    /// if you intend to iterate more than once in performance-sensitive
    /// code.
    @objc public static var all: [Flag] {
        return supportedCountryCodes.compactMap { Flag(countryCode: $0) }
    }
}
