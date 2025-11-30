// src/screens/SearchScreen.tsx
import React, { useState, useEffect } from "react";
import {
  View, Text, TextInput, TouchableOpacity, ActivityIndicator,
  FlatList, Image
} from "react-native";
import { searchKeyword, searchTitle } from "../api";
import { API_BASE } from "../config";
import { toBool, toNum } from "../../utils/normalize";

export default function SearchScreen({ navigation, route }) {
  const restored = route.params?.restoredSearch;

  const [query, setQuery] = useState(restored?.query || "");
  const [mode, setMode] = useState(restored?.mode || "keyword");
  const [advanced, setAdvanced] = useState(toBool(restored?.advanced) || false);
  const [rankMode, setRankMode] = useState(restored?.rankMode || "tf");
  const [page, setPage] = useState(toNum(restored?.page, 1));

  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  const pageSize = 20;

  const runSearch = async (p = page) => {
    if (!query.trim()) return;
    setLoading(true);

    let data;
    if (mode === "title") {
      data = await searchTitle(query, p, pageSize);
    } else {
      data = await searchKeyword(query, advanced, rankMode, p, pageSize);
    }

    setResults(data.results || []);
    setTotal(data.total || 0);
    setLoading(false);
  };

  useEffect(() => {
    if (restored) runSearch(page);
  }, []);

  return (
    <View style={{ padding: 16, flex: 1 }}>
      <Text
        style={{
          fontSize: 28,
          fontWeight: "bold",
          marginBottom: 20,
          textAlign: "center",
        }}
        onPress={() => {
          setQuery("");
          setPage(1);
          setResults([]);
          setTotal(0);
        }}
      >
        Book Search Engine
      </Text>

      {/* Search box */}
      <TextInput
        value={query}
        onChangeText={setQuery}
        placeholder={
          mode === "title"
            ? "Search title, author..."
            : advanced
            ? "Regex content..."
            : "Keyword..."
        }
        style={{
          borderWidth: 1,
          borderColor: "#aaa",
          padding: 10,
          borderRadius: 10,
          marginBottom: 10,
        }}
      />

      <TouchableOpacity
        onPress={() => {
          setPage(1);
          runSearch(1);
        }}
        style={{
          backgroundColor: "#0077ff",
          padding: 12,
          borderRadius: 10,
          marginBottom: 15,
        }}
      >
        <Text style={{ color: "white", textAlign: "center", fontSize: 16 }}>
          Search
        </Text>
      </TouchableOpacity>

      {/* Mode selection */}
      <View style={{ flexDirection: "row", marginBottom: 10 }}>
        <Text style={{ marginRight: 10, padding: 5 }}>Search by:</Text>

        {["keyword", "title"].map((m) => (
          <TouchableOpacity
            key={m}
            onPress={() => setMode(m)}
            style={{
              padding: 8,
              backgroundColor: mode === m ? "#0077ff" : "#ccc",
              borderRadius: 6,
              marginRight: 10,
            }}
          >
            <Text style={{ color: "white" }}>{m}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Ranking mode */}
      {mode === "keyword" && (
        <View style={{ flexDirection: "row", marginBottom: 10 }}>
          <Text style={{ marginRight: 10, padding: 5 }}>Rank:</Text>

          {["tf", "pr", "tfpr"].map((rm) => (
            <TouchableOpacity
              key={rm}
              onPress={() => setRankMode(rm)}
              style={{
                padding: 6,
                marginRight: 8,
                backgroundColor: rankMode === rm ? "#444" : "#ccc",
                borderRadius: 6,
              }}
            >
              <Text style={{ color: "white" }}>{rm.toUpperCase()}</Text>
            </TouchableOpacity>
          ))}
        </View>
      )}

      {/* Regex toggle */}
      {mode === "keyword" && (
        <TouchableOpacity
          onPress={() => setAdvanced((a) => !a)}
          style={{
            padding: 8,
            backgroundColor: advanced ? "#0077ff" : "#ccc",
            borderRadius: 8,
            marginBottom: 10,
          }}
        >
          <Text style={{ color: "white" }}>
            Regex: {advanced ? "ON" : "OFF"}
          </Text>
        </TouchableOpacity>
      )}

      {loading && <ActivityIndicator size="large" />}

      {/* Results */}
      <FlatList
        data={results}
        keyExtractor={(item) => item.book_id.toString()}
        renderItem={({ item }) => (
          <TouchableOpacity
            onPress={() =>
              navigation.navigate("Book", {
                id: item.book_id,
                fromSearch: {
                  query,
                  page,
                  mode,
                  advanced,
                  rankMode,
                },
              })
            }
            style={{
              flexDirection: "row",
              paddingVertical: 12,
              borderBottomWidth: 1,
              borderColor: "#ddd",
            }}
          >
            {item.cover_url && (
              <Image
                source={{ uri: API_BASE + item.cover_url }}
                style={{
                  width: 80,
                  height: 120,
                  marginRight: 12,
                  borderRadius: 6,
                  resizeMode: "contain",
                }}
              />
            )}

            <View style={{ flex: 1 }}>
              <Text style={{ fontWeight: "bold", fontSize: 16 }}>
                {item.title}
              </Text>
              <Text numberOfLines={3}>{item.snippet}</Text>

              <Text style={{ marginTop: 6 }}>
                TF: {item.tf} · PR: {item.pagerank.toFixed(6)}
              </Text>
              <Text style={{ color: "#0077ff" }}>
                Score: {item.score.toFixed(6)}
              </Text>
            </View>
          </TouchableOpacity>
        )}
      />
    </View>
  );
}
