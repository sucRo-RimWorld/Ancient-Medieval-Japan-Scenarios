Feature: Independent Scenarios - vanilla

  Scenario: Scenarios vanilla requested providers
    Then Scenario vanilla uses the requested providers

  Scenario: Scenarios vanilla loaded village definition
    Then loaded New Village scenario matches the start design

  @quickstart:AmjScenarioVillageQuickstart
  Scenario: Scenarios vanilla actual village start
    Then New Village starts with five villagers and the designed supplies
