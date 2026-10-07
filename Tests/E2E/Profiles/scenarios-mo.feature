Feature: Independent Scenarios - mo

  Scenario: Scenarios mo requested providers
    Then Scenario mo uses the requested providers

  Scenario: Scenarios mo loaded village definition
    Then loaded New Village scenario matches the start design

  @quickstart:AmjScenarioVillageQuickstart
  Scenario: Scenarios mo actual village start
    Then New Village starts with five villagers and the designed supplies
