// src/screens/MobileReadScreen.tsx
import React, { useEffect, useState } from "react";
import {
  View, Text, TouchableOpacity, ScrollView, ActivityIndicator
} from "react-native";
import axios from "axios";
import { useRoute } from "@react-navigation/native";
import { API_BASE } from "../config";
import { toNum } from "../../utils/normalize";

export default function ReadScreen() {
  const route = useRoute();
  const id = toNum(route.params?.id);
  const [page, setPage] = useState(1);
  const [pageData, setPageData] = useState(null);

  const [dark, setDark] = useState(false);
  const [fontSize, setFontSize] = useState(18);

  useEffect(() => {
    axios
      .get(`${API_BASE}/book-page/${id}`, { params: { page, size: 4000 } })
      .then((r) => setPageData(r.data));
  }, [id, page]);

  if (!pageData)
    return <ActivityIndicator size="large" style={{ marginTop: 40 }} />;

  return (
    <View
      style={{
        flex: 1,
        backgroundColor: dark ? "#111" : "#f7f7f7",
        padding: 16,
      }}
    >
      <Text
        style={{
          textAlign: "center",
          marginVertical: 10,
          fontSize: 22,
          color: dark ? "#eee" : "#222",
        }}
      >
        {pageData.title}
      </Text>

      {/* Controls */}
      <View
        style={{
          flexDirection: "row",
          justifyContent: "center",
          marginBottom: 10,
        }}
      >
        <TouchableOpacity onPress={() => setFontSize((f) => Math.max(12, f - 2))}>
          <Text style={{ color: dark ? "#fff" : "#000", fontSize: 18 }}>A−</Text>
        </TouchableOpacity>

        <TouchableOpacity onPress={() => setFontSize((f) => f + 2)}>
          <Text style={{ color: dark ? "#fff" : "#000", fontSize: 18 }}>A+</Text>
        </TouchableOpacity>

        <TouchableOpacity onPress={() => setDark(!dark)}>
          <Text style={{ color: dark ? "#fff" : "#000", fontSize: 18 }}>
            {dark ? "☀ Light" : "🌙 Dark"}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      <ScrollView
        style={{
          flex: 1,
          padding: 18,
          backgroundColor: dark ? "#1a1a1a" : "#fff",
          borderRadius: 6,
        }}
      >
        <Text
          style={{
            color: dark ? "#eee" : "#222",
            fontSize: fontSize,
            lineHeight: fontSize * 1.6,
          }}
        >
          {pageData.text}
        </Text>
      </ScrollView>

      {/* Footer */}
      <View style={{ alignItems: "center", marginTop: 16 }}>
        <Text style={{ color: dark ? "#eee" : "#222" }}>
          Page {page} / {pageData.total_pages}
        </Text>

        <View style={{ flexDirection: "row", marginTop: 8 }}>
          <TouchableOpacity disabled={page <= 1} onPress={() => setPage(page - 1)}>
            <Text style={{ fontSize: 20, color: page <= 1 ? "#888" : "#0077ff" }}>
              ⬅ Prev
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            disabled={page >= pageData.total_pages}
            onPress={() => setPage(page + 1)}
            style={{ marginLeft: 20 }}
          >
            <Text
              style={{
                fontSize: 20,
                color: page >= pageData.total_pages ? "#888" : "#0077ff",
              }}
            >
              Next ➡
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}
