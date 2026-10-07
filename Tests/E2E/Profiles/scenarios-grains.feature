Feature: Independent Scenarios - grains

  Scenario: Scenarios grains requested providers
    Then Scenario grains uses the requested providers

  Scenario: Scenarios grains loaded village definition
    Then loaded New Village scenario matches the start design

  @quickstart:AmjScenarioVillageQuickstart
  Scenario: Scenarios grains actual village start
    Then New Village starts with five villagers and the designed supplies
