import { databaseConfig } from "./db_config";
import neo4j from "neo4j-driver";
import { inferSchema } from "neo4j-graphql-js";
const fs = require("fs");

const driver = neo4j.driver(
  databaseConfig.uri,
  neo4j.auth.basic(databaseConfig.user, databaseConfig.password),
  {
    encrypted: false ? "ENCRYPTION_ON" : "ENCRYPTION_OFF",
    logging: neo4j.logging.console("debug"),
  }
);

/*
 * Generate schema from existing database
 */
const schemaInferenceOptions = {
  alwaysIncludeRelationships: false,
};

inferSchema(driver, schemaInferenceOptions).then((result) => {
  console.log(result);
  fs.writeFile("schema.graphql", result.typeDefs, (err) => {
    if (err) throw err;
    console.log("Updated schema.graphql");
    process.exit(0);
  });
});
