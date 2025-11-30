// src/screens/BookScreen.tsx
import React, { useEffect, useState } from "react";
import {
  View, Text, Image, TouchableOpacity,
  ScrollView, ActivityIndicator
} from "react-native";
import { useRoute, useNavigation } from "@react-navigation/native";
import { getBook, getRecommendations } from "../api";
import { API_BASE } from "../config";

export default function BookScreen() {
  const route = useRoute();
  const navigation = useNavigation();

  const { id, fromSearch } = route.params || {};
  const bookId = Number(id);

  const [book, setBook] = useState(null);
  const [recs, setRecs] = useState([]);

  useEffect(() => {
    getBook(bookId).then(setBook);
    getRecommendations(bookId).then((d) => setRecs(d.recommendations));
  }, [bookId]);

  if (!book) return <ActivityIndicator size="large" style={{ marginTop: 40 }} />;

  return (
    <ScrollView style={{ padding: 16 }}>
      <Text
        style={{ fontSize: 26, fontWeight: "bold", textAlign: "center" }}
      >
        {book.title}
      </Text>

      {book.authors && (
        <Text style={{ textAlign: "center", color: "#444", marginBottom: 10 }}>
          {book.authors.join(", ")}
        </Text>
      )}

      <View style={{ alignItems: "center", marginVertical: 20 }}>
        {book.cover_url && (
          <Image
            source={{ uri: API_BASE + book.cover_url }}
            style={{
              width: 200,
              height: 260,
              resizeMode: "contain",
              borderRadius: 6,
            }}
          />
        )}
      </View>

      <Text style={{ fontSize: 16, lineHeight: 22, marginBottom: 20 }}>
        {book.summary || "No summary available."}
      </Text>

      <TouchableOpacity
        onPress={() =>
          navigation.navigate("Read", {
            id: bookId,
          })
        }
        style={{
          backgroundColor: "#0077ff",
          padding: 12,
          borderRadius: 10,
          alignSelf: "center",
          marginBottom: 30,
        }}
      >
        <Text style={{ color: "white", fontSize: 18 }}>📖 Read this book</Text>
      </TouchableOpacity>

      <Text style={{ fontSize: 22, marginBottom: 10 }}>📚 Similar Books</Text>

      {recs.map((r) => (
        <TouchableOpacity
          key={r.book_id}
          onPress={() =>
            navigation.navigate("Book", {
              id: r.book_id,
            })
          }
          style={{
            flexDirection: "row",
            paddingVertical: 10,
            borderBottomWidth: 1,
            borderColor: "#ddd",
          }}
        >
          {r.cover_url && (
            <Image
              source={{ uri: API_BASE + r.cover_url }}
              style={{
                width: 70,
                height: 100,
                marginRight: 12,
                resizeMode: "contain",
                borderRadius: 6,
              }}
            />
          )}

          <View style={{ flex: 1 }}>
            <Text style={{ fontSize: 16, fontWeight: "bold" }}>
              {r.title}
            </Text>
            <Text style={{ color: "#555" }}>
              Similarity: {r.score.toFixed(4)}
            </Text>
          </View>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
}
