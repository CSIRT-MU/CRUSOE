export const initializeDatabase = (driver) => {
  const initCypher = `CALL apoc.schema.assert({}, {})`

  const executeQuery = (driver) => {
    const session = driver.session()
    return session
      .writeTransaction((tx) => tx.run(initCypher))
      .then()
      .finally(() => session.close())
  }

  executeQuery(driver).catch((error) => {
    console.error('Database initialization failed to complete\n', error.message)
  })
}
