import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";

import SearchScreen from "./src/screens/SearchScreen";
import BookScreen from "./src/screens/BookScreen";
import ReadScreen from "./src/screens/MobileReadScreen";

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Search">
        <Stack.Screen name="Search" component={SearchScreen} />
        <Stack.Screen name="Book" component={BookScreen} />
        <Stack.Screen name="Read" component={ReadScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
