Feature: Independent Scenarios - grains-mo

  Scenario: Scenarios grains-mo requested providers
    Then Scenario grains-mo uses the requested providers

  Scenario: Scenarios grains-mo loaded village definition
    Then loaded New Village scenario matches the start design

  @quickstart:AmjScenarioVillageQuickstart
  Scenario: Scenarios grains-mo actual village start
    Then New Village starts with five villagers and the designed supplies
